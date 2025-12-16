from apscheduler.schedulers.background import BackgroundScheduler
from app.services.twitter import TwitterClient
from app.services.llm import llm_service
from app.services.telegram import send_telegram_message
from app.database import SessionLocal
from app.models import Tweet, TwitterList, SystemSetting
from app.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def get_check_interval():
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == "check_interval_minutes").first()
        if setting:
            return int(setting.value)
        return settings.AUTOMATION_CHECK_INTERVAL_MINUTES
    except Exception:
        return settings.AUTOMATION_CHECK_INTERVAL_MINUTES
    finally:
        db.close()

def update_job_interval(minutes: int):
    try:
        scheduler.reschedule_job('check_lists_job', trigger='interval', minutes=minutes)
        logger.info(f"Rescheduled job to run every {minutes} minutes")
        return True
    except Exception as e:
        logger.error(f"Failed to reschedule job: {e}")
        return False

def check_lists():
    logger.info("Starting scheduled check...")
    db = SessionLocal()
    try:
        # Sync lists from config
        config_urls = [url.strip() for url in settings.TWITTER_LIST_URLS.split(",") if url.strip()]
        for url in config_urls:
            exists = db.query(TwitterList).filter(TwitterList.url == url).first()
            if not exists:
                logger.info(f"Adding new list from config: {url}")
                db.add(TwitterList(url=url))
        db.commit()
            
        lists = db.query(TwitterList).all()
        client = TwitterClient(settings.TWITTER_AUTH_TOKEN, settings.TWITTER_CT0_TOKEN)
        
        # Fetching Phase
        for lst in lists:
            try:
                list_id = client.extract_list_id(lst.url)
                if not list_id:
                    logger.warning(f"Could not extract ID for {lst.url}")
                    continue
                    
                tweets = client.get_list_tweets(list_id)
                
                for t in tweets:
                    # Check if exists
                    exists = db.query(Tweet).filter(Tweet.tweet_id == t['id']).first()
                    if exists:
                        continue
                    
                    # Save immediately without analysis
                    new_tweet = Tweet(
                        tweet_id=t['id'],
                        author_name=t['author_name'],
                        author_handle=t['author_handle'],
                        content=t['text'],
                        created_at=datetime.strptime(t['created_at'], '%a %b %d %H:%M:%S +0000 %Y'),
                        relevance_score=0.0,
                        analysis_summary=None # Mark as pending analysis
                    )
                    db.add(new_tweet)
                        
                lst.last_scraped_at = datetime.now()
                db.commit()
            except Exception as e:
                logger.error(f"Error processing list {lst.url}: {e}")
                db.rollback()

        # Analysis Phase
        try:
            # Process pending analysis
            pending_tweets = db.query(Tweet).filter(Tweet.analysis_summary == None).all()
            if pending_tweets:
                logger.info(f"Found {len(pending_tweets)} tweets pending analysis")
            
            for tweet in pending_tweets:
                try:
                    # Analyze
                    analysis = llm_service.analyze_tweet(tweet.content, prompt_template=settings.DEFAULT_PROMPT)
                    score = analysis.get('score', 0.0)
                    translation = analysis.get('translation', '').strip()
                    summary = analysis.get('summary', '').strip()
                    combined_summary = "\n".join([text for text in [translation, summary] if text]).strip()
                    if not translation and summary.startswith("翻译："):
                        # Backward compatibility with older prompt
                        translation = summary
                        summary = ''
                        combined_summary = translation
                    
                    tweet.relevance_score = score
                    tweet.analysis_summary = combined_summary or summary or translation
                    
                    # Notify
                    if score >= settings.DEFAULT_SCORE_THRESHOLD:
                        msg = f"🚨 *发现高价值推文* (评分: {score})\n\n"
                        msg += f"👤 {tweet.author_name} (@{tweet.author_handle})\n"
                        if translation:
                            msg += f"📝 {translation}\n"
                        if summary:
                            msg += f"🧾 {summary}\n"
                        if not translation and not summary and tweet.analysis_summary:
                            msg += f"📝 {tweet.analysis_summary}\n"
                        msg += "\n"
                        msg += f"🔗 https://x.com/{tweet.author_handle}/status/{tweet.tweet_id}"
                        send_telegram_message(msg)
                        tweet.is_sent_to_telegram = True
                    
                    db.commit()
                except Exception as e:
                    logger.error(f"Error analyzing tweet {tweet.id}: {e}")
        except Exception as e:
            logger.error(f"Error in analysis phase: {e}")
            
    except Exception as e:
        logger.error(f"Critical error in scheduler: {e}")
    finally:
        db.close()

def start_scheduler():
    interval = get_check_interval()
    logger.info(f"Starting scheduler with interval: {interval} minutes")
    # Run immediately on start, then every X minutes
    scheduler.add_job(check_lists, 'interval', minutes=interval, next_run_time=datetime.now(), id='check_lists_job')
    scheduler.start()
