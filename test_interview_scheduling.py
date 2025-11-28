#!/usr/bin/env python3
"""
Test interview scheduling functionality
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agents.interview_scheduler_agent import InterviewSchedulerAgent

async def test_interview_scheduling():
    """Test the interview scheduler"""

    print("=" * 70)
    print("TESTING INTERVIEW SCHEDULING")
    print("=" * 70)

    # Create test candidate data
    candidates = [{
        'id': 'test_candidate_1',
        'name': 'Md Aamir Khan',
        'email': 'mdaamirkhan7186@gmail.com',
        'phone': '+918240968108',
        'overall_score': 85.0,
        'tier': 'strong_match'
    }]

    print(f"\n[1/3] Test Data:")
    print(f"   Candidate: {candidates[0]['name']}")
    print(f"   Email: {candidates[0]['email']}")
    print(f"   Score: {candidates[0]['overall_score']}%")

    print(f"\n[2/3] Initializing InterviewSchedulerAgent...")
    try:
        scheduler = InterviewSchedulerAgent()
        print("   ✅ Agent initialized")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return

    print(f"\n[3/3] Attempting to schedule interview...")
    print("   (This will create a real calendar event and send email)")
    print("   Interviewer: souveek29@gmail.com")

    try:
        result = await scheduler.process({
            'candidates': candidates,
            'interviewer_email': 'souveek29@gmail.com',
            'duration_minutes': 60
        })

        if result['status'] == 'success':
            scheduled = result.get('scheduled_slots', [])
            print(f"\n✅ SUCCESS: Scheduled {len(scheduled)} interview(s)")

            if scheduled:
                interview = scheduled[0]
                print(f"\n   Interview Details:")
                print(f"   - Candidate: {interview['candidate_name']}")
                print(f"   - Start Time: {interview['start_time']}")
                print(f"   - Status: {interview['status']}")
                print(f"   - Calendar Event ID: {interview.get('calendar_event_id')}")

                print(f"\n   ✅ Check your Google Calendar for the event!")
                print(f"   ✅ Check {interview['candidate_email']} for invitation email!")
            else:
                print("\n   ⚠️  No interviews scheduled (may have failed)")
                print(f"   Message: {result.get('message', 'Unknown')}")
        else:
            print(f"\n❌ FAILED: {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_interview_scheduling())
