"""
Email Service

Handles sending emails for interview invitations, notifications, and updates.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True
    ):
        """
        Initialize email service
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username (usually email address)
            password: SMTP password or app-specific password
            use_tls: Whether to use TLS encryption
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        
        logger.info(f"Email service initialized for {smtp_host}:{smtp_port}")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        html: bool = False,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (text or HTML)
            cc: List of CC recipients
            bcc: List of BCC recipients
            html: Whether body is HTML (default: plain text)
            attachments: List of file paths to attach
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to_email
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Add timestamp
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Attach body
            if html:
                part = MIMEText(body, 'html')
            else:
                part = MIMEText(body, 'plain')
            
            msg.attach(part)
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    self._add_attachment(msg, file_path)
            
            # Send email
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.username, self.password)
                server.send_message(msg, self.username, recipients)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check username and password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """
        Add attachment to email message
        
        Args:
            msg: Email message object
            file_path: Path to file to attach
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.warning(f"Attachment not found: {file_path}")
                return
            
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {path.name}'
            )
            
            msg.attach(part)
            logger.debug(f"Added attachment: {path.name}")
            
        except Exception as e:
            logger.error(f"Failed to add attachment {file_path}: {str(e)}")
    
    def send_interview_invitation(
        self,
        candidate_email: str,
        candidate_name: str,
        interview_date: str,
        interview_time: str,
        interviewer_name: str,
        position_title: str,
        meeting_link: Optional[str] = None,
        duration_minutes: int = 60,
        additional_info: Optional[str] = None
    ) -> bool:
        """
        Send interview invitation email
        
        Args:
            candidate_email: Candidate's email
            candidate_name: Candidate's name
            interview_date: Interview date (formatted)
            interview_time: Interview time (formatted)
            interviewer_name: Interviewer's name
            position_title: Job position title
            meeting_link: Video conference link (optional)
            duration_minutes: Interview duration
            additional_info: Additional instructions
            
        Returns:
            True if sent successfully
        """
        subject = f"Interview Invitation - {position_title}"
        
        body = f"""Dear {candidate_name},

We are pleased to invite you for an interview for the {position_title} position.

Interview Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {interview_date}
🕐 Time: {interview_time}
⏱️ Duration: {duration_minutes} minutes
👤 Interviewer: {interviewer_name}
"""
        
        if meeting_link:
            body += f"\n🔗 Meeting Link: {meeting_link}\n"
        
        body += """
What to Expect:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This interview will be an opportunity for us to learn more about your experience and for you to learn more about the role and our team.
"""
        
        if additional_info:
            body += f"\n{additional_info}\n"
        
        body += """
Preparation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Please review the job description
- Prepare questions you have about the role
- Test your video/audio setup if applicable
- Have a copy of your resume handy

Please confirm your attendance by replying to this email.

If you need to reschedule, please let us know as soon as possible.

We look forward to speaking with you!

Best regards,
Recruitment Team
"""
        
        return self.send_email(candidate_email, subject, body)
    
    def send_interview_reminder(
        self,
        candidate_email: str,
        candidate_name: str,
        interview_date: str,
        interview_time: str,
        meeting_link: Optional[str] = None
    ) -> bool:
        """
        Send interview reminder email
        
        Args:
            candidate_email: Candidate's email
            candidate_name: Candidate's name
            interview_date: Interview date
            interview_time: Interview time
            meeting_link: Video conference link
            
        Returns:
            True if sent successfully
        """
        subject = f"Reminder: Interview Tomorrow"
        
        body = f"""Hi {candidate_name},

This is a friendly reminder about your interview scheduled for tomorrow.

Interview Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {interview_date}
🕐 Time: {interview_time}
"""
        
        if meeting_link:
            body += f"🔗 Meeting Link: {meeting_link}\n"
        
        body += """
Quick Checklist:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Test your video/audio setup
□ Review the job description
□ Prepare your questions
□ Have a notepad ready
□ Join 5 minutes early

Looking forward to meeting you!

Best regards,
Recruitment Team
"""
        
        return self.send_email(candidate_email, subject, body)
    
    def send_rejection_email(
        self,
        candidate_email: str,
        candidate_name: str,
        position_title: str,
        feedback: Optional[str] = None
    ) -> bool:
        """
        Send rejection email with constructive feedback
        
        Args:
            candidate_email: Candidate's email
            candidate_name: Candidate's name
            position_title: Job position title
            feedback: Optional constructive feedback
            
        Returns:
            True if sent successfully
        """
        subject = f"Application Update - {position_title}"
        
        body = f"""Dear {candidate_name},

Thank you for your interest in the {position_title} position and for taking the time to apply.

After careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current needs.
"""
        
        if feedback:
            body += f"\n{feedback}\n"
        
        body += """
We were impressed by your background and encourage you to apply for future positions that match your skills and experience.

We wish you all the best in your job search.

Best regards,
Recruitment Team
"""
        
        return self.send_email(candidate_email, subject, body)
    
    def send_test_email(self, to_email: str) -> bool:
        """
        Send a test email to verify configuration
        
        Args:
            to_email: Recipient email address
            
        Returns:
            True if sent successfully
        """
        subject = "Test Email - Recruitment System"
        body = """This is a test email from the Intelligent Recruitment System.

If you received this email, the email service is configured correctly.

Test Details:
- SMTP Host: {}
- SMTP Port: {}
- From: {}

Timestamp: {}
""".format(
            self.smtp_host,
            self.smtp_port,
            self.username,
            datetime.now().isoformat()
        )
        
        return self.send_email(to_email, subject, body)


def create_email_service_from_config(config) -> EmailService:
    """
    Create EmailService instance from configuration
    
    Args:
        config: Configuration object with SMTP settings
        
    Returns:
        EmailService instance
    """
    return EmailService(
        smtp_host=config.SMTP_HOST,
        smtp_port=config.SMTP_PORT,
        username=config.SMTP_USER,
        password=config.SMTP_PASSWORD
    )