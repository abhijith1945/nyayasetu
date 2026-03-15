"""
Email Notification Service
Sends automated alerts for crisis situations to officers
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

# Gmail SMTP Configuration
GMAIL_SENDER = os.getenv("GMAIL_SENDER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")  # App-specific password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


async def send_crisis_alert_email(
    officer_email: str,
    officer_name: str,
    crisis_data: Dict,
    grievance_data: Dict
) -> bool:
    """
    Send urgent crisis alert email to officer
    
    Args:
        officer_email: Officer's email address
        officer_name: Officer's name
        crisis_data: {
            "crisis_type": "health_emergency|multiple_ward_complaints|system_failure",
            "severity": "critical|high|medium",
            "description": "what happened",
            "affected_count": number of people affected
        }
        grievance_data: The grievance that triggered the alert
    
    Returns:
        bool: True if sent successfully
    """
    try:
        if not GMAIL_SENDER or not GMAIL_PASSWORD:
            logger.warning("Gmail credentials not configured - skipping email send")
            return False
        
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 URGENT CRISIS ALERT: {crisis_data.get('crisis_type', 'UNKNOWN')}"
        msg["From"] = GMAIL_SENDER
        msg["To"] = officer_email
        
        # HTML email body
        html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 8px; overflow: hidden;">
      <div style="background-color: #fee; border-left: 4px solid #f00; padding: 20px;">
        <h2 style="color: #f00; margin-top: 0;">🚨 URGENT CRISIS DETECTED</h2>
        
        <p><strong>Dear {officer_name},</strong></p>
        <p>An urgent situation has been detected in your assigned area that requires immediate action.</p>
        
        <div style="background-color: #fdd; padding: 15px; border-radius: 4px; margin: 20px 0;">
          <p><strong>Alert Type:</strong> {crisis_data.get('crisis_type', 'Unknown')}</p>
          <p><strong>Severity Level:</strong> <span style="color: #f00; font-weight: bold; font-size: 16px;">{crisis_data.get('severity', 'Unknown').upper()}</span></p>
          <p><strong>Description:</strong></p>
          <p style="margin: 10px 0;">{crisis_data.get('description', 'No description provided')}</p>
        </div>
        
        <h3>Grievance Information:</h3>
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Grievance ID:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{grievance_data.get('id', 'N/A')}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Ward:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{grievance_data.get('ward', 'Unknown')}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Category:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{grievance_data.get('category', 'General')}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Contact:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{grievance_data.get('phone', 'Not provided')}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Affected Count:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{crisis_data.get('affected_count', 1)}</td>
          </tr>
        </table>
        
        <h3>Complaint Details:</h3>
        <blockquote style="background-color: #f9f9f9; padding: 12px; border-left: 3px solid #ccc; margin: 10px 0;">
          {grievance_data.get('description', 'No description')}
        </blockquote>
        
        <h3>✅ Required Actions (Within 1 Hour):</h3>
        <ol style="line-height: 1.8;">
          <li>Acknowledge receipt of this alert</li>
          <li>Contact affected citizen immediately at {grievance_data.get('phone', 'provided number')}</li>
          <li>Assess situation severity</li>
          <li>Escalate to relevant department if needed</li>
          <li>Update grievance status in NyayaSetu dashboard</li>
        </ol>
        
        <p style="color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
          <strong>This is an automated alert from NyayaSetu Crisis Management System.</strong><br>
          Your prompt action is critical to public safety. If you have any issues, contact your administrator.
        </p>
      </div>
    </div>
  </body>
</html>
"""
        
        # Attach HTML part
        msg.attach(MIMEText(html_body, "html"))
        
        # Send email
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send_smtp_sync, msg)
        
        logger.info(f"✅ Crisis alert email sent to {officer_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send crisis alert email: {e}")
        return False


def _send_smtp_sync(msg):
    """Synchronous SMTP send (run in executor)"""
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_SENDER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logger.error(f"SMTP error: {e}")
        raise


async def send_dataset_issue_notification(
    admin_email: str,
    issue_data: Dict
) -> bool:
    """
    Send notification about detected dataset issues
    
    Args:
        admin_email: Admin email
        issue_data: {
            "issue_type": "missing_values|duplicates|inconsistency|invalid_format",
            "table": "table_name",
            "affected_records": count,
            "auto_fixed": bool,
            "fix_details": "what was fixed"
        }
    """
    try:
        if not GMAIL_SENDER or not GMAIL_PASSWORD:
            logger.warning("Gmail credentials not configured")
            return False
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"📊 Dataset Issue Alert: {issue_data.get('issue_type', 'UNKNOWN')}"
        msg["From"] = GMAIL_SENDER
        msg["To"] = admin_email
        
        fixed_status = "✅ AUTO-FIXED" if issue_data.get("auto_fixed") else "⚠️ MANUAL REVIEW NEEDED"
        
        html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 8px; overflow: hidden;">
      <div style="background-color: #eef; border-left: 4px solid #00a; padding: 20px;">
        <h2 style="color: #00a; margin-top: 0;">📊 Dataset Issue Detected & Remediated</h2>
        
        <p><strong>Issue Type:</strong> {issue_data.get('issue_type', 'Unknown')}</p>
        <p><strong>Table Affected:</strong> {issue_data.get('table', 'Unknown')}</p>
        <p><strong>Records Affected:</strong> {issue_data.get('affected_records', 0)}</p>
        <p><strong>Status:</strong> <span style="font-weight: bold; color: {'green' if issue_data.get('auto_fixed') else 'orange'};">{fixed_status}</span></p>
        
        <h3>Remediation Details:</h3>
        <pre style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto;">
{issue_data.get('fix_details', 'No details provided')}
        </pre>
        
        <p style="color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
          Automated by NyayaSetu Data Integrity Agent
        </p>
      </div>
    </div>
  </body>
</html>
"""
        
        msg.attach(MIMEText(html_body, "html"))
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send_smtp_sync, msg)
        
        logger.info(f"✅ Dataset alert sent to {admin_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send dataset notification: {e}")
        return False


def send_email_smtp(
    to_email: str,
    subject: str,
    html_content: str,
    plain_text: Optional[str] = None
) -> bool:
    """
    Generic email sender via SMTP (synchronous)
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_content: HTML formatted email body
        plain_text: Optional plain text alternative
    
    Returns:
        bool: True if sent successfully
    """
    try:
        if not GMAIL_SENDER or not GMAIL_PASSWORD:
            logger.warning("Gmail credentials not configured - skipping email send")
            return False
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = GMAIL_SENDER
        msg["To"] = to_email
        
        # Attach plain text part if provided, otherwise use simplified HTML
        if plain_text:
            msg.attach(MIMEText(plain_text, "plain"))
        
        # Attach HTML part
        msg.attach(MIMEText(html_content, "html"))
        
        # Send via SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_SENDER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"✅ Email sent to {to_email} with subject: {subject}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Gmail authentication failed: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
