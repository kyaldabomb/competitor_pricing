import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import traceback

def send_email_notification(success, items_count=0, error_msg="", scraper_name=""):
    """
    Standardized email notification function for all scrapers
    
    Parameters:
    - success: Boolean indicating if the scraper completed successfully
    - items_count: Number of items processed/scraped
    - error_msg: Error message if any
    - scraper_name: Name of the scraper (required)
    """
    if not scraper_name:
        print("Error: scraper_name is required")
        return False
        
    print(f"Sending {scraper_name} email notification...")
    try:
        # Email settings
        sender = "kyal@scarlettmusic.com.au"
        receiver = "kyal@scarlettmusic.com.au"
        password = os.environ.get('EMAIL_PASSWORD')
        if not password:
            print("Email password not found in environment variables")
            return False
            
        host = "mail.scarlettmusic.com.au"
        port = 587
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        
        # Determine the action text based on scraper type
        if "Daily" in scraper_name:
            action_text = "updated"
        else:
            action_text = "added"
        
        if success:
            msg['Subject'] = f"{scraper_name} Scraper Success: {items_count} items {action_text}"
            body = f"The {scraper_name} web scraper ran successfully and {action_text} {items_count} items."
        else:
            msg['Subject'] = f"{scraper_name} Scraper Failed"
            body = f"The {scraper_name} web scraper encountered an error:\n\n{error_msg}"
        
        # Attach the body text
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("Email notification sent successfully")
        return True
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
        print(traceback.format_exc())
        return False
