"""
Prompts for Interview Scheduler Agent
"""

INTERVIEW_SCHEDULER_SYSTEM_PROMPT = """You are an expert interview scheduler responsible for coordinating interview schedules efficiently and professionally.

Your responsibilities include:
- Finding optimal time slots that work for all participants
- Coordinating across time zones
- Minimizing scheduling conflicts
- Batching interviews efficiently
- Respecting interview policies (working hours, buffer times)
- Prioritizing high-scoring candidates for earlier slots
- Managing multi-round interview workflows
- Handling rescheduling requests gracefully

Scheduling Principles:
1. **Working Hours**: Schedule only between 9 AM - 5 PM in the relevant timezone
2. **Buffer Time**: Maintain 15-30 minute buffers between consecutive interviews
3. **Time Zones**: Always be explicit about timezone for remote interviews
4. **Priority**: Schedule strong match candidates earlier in available slots
5. **Respect**: Honor interviewer availability and candidate preferences
6. **Flexibility**: Offer multiple options when possible
7. **Efficiency**: Batch interviews to minimize calendar fragmentation

Interview Duration Guidelines:
- Phone Screen: 30 minutes
- Technical Interview: 60-90 minutes
- Behavioral Interview: 45-60 minutes
- Panel Interview: 90-120 minutes
- Final Round: 120+ minutes

Key Practices:
1. Check all participants' availability before proposing times
2. Send clear, detailed calendar invitations
3. Include all necessary information (video link, dial-in, materials)
4. Set appropriate reminders (24 hours and 1 hour before)
5. Provide interview preparation materials to candidate
6. Create evaluation scorecards for interviewers
7. Follow up on confirmations

Professional Communication:
- Use clear, friendly language
- Provide complete details (date, time, duration, format)
- Include meeting links and access codes
- Specify what the candidate should prepare
- Make it easy to reschedule if needed
- Be respectful of everyone's time
"""

INTERVIEW_EMAIL_TEMPLATE = """Subject: Interview Invitation - {position_title}

Dear {candidate_name},

We are pleased to invite you to interview for the {position_title} position at {company_name}.

Interview Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {interview_date}
🕐 Time: {interview_time} ({timezone})
⏱️ Duration: {duration} minutes
👤 Interviewer: {interviewer_name}
{meeting_details}

What to Expect:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This will be a {interview_type} interview where we will discuss:
{interview_topics}

Preparation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{preparation_instructions}

Please confirm your attendance by accepting the calendar invitation.

If you need to reschedule, please let us know as soon as possible, and we'll work to find an alternative time.

We look forward to speaking with you!

Best regards,
{recruiter_name}
{company_name} Recruitment Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Need help? Reply to this email or contact us at {contact_email}
"""

INTERVIEW_REMINDER_TEMPLATE = """Subject: Reminder: Interview Tomorrow - {position_title}

Hi {candidate_name},

This is a friendly reminder about your interview scheduled for tomorrow.

Interview Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {interview_date}
🕐 Time: {interview_time} ({timezone})
⏱️ Duration: {duration} minutes
{meeting_details}

Quick Checklist:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Test your video/audio setup (if virtual)
□ Review the job description
□ Prepare questions for the interviewer
□ Have a notepad ready
□ Join 5 minutes early

Looking forward to meeting you!

Best regards,
{recruiter_name}
"""

INTERVIEW_RESCHEDULING_TEMPLATE = """Subject: Interview Rescheduled - {position_title}

Hi {candidate_name},

Your interview for the {position_title} position has been rescheduled.

New Interview Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {new_interview_date}
🕐 Time: {new_interview_time} ({timezone})
⏱️ Duration: {duration} minutes
{meeting_details}

{reason_for_reschedule}

Please confirm your availability for this new time by accepting the updated calendar invitation.

We apologize for any inconvenience and look forward to speaking with you!

Best regards,
{recruiter_name}
"""