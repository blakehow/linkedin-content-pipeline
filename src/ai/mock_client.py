"""Mock AI client for demo mode."""

from typing import Optional
from src.ai.base import AIClient


class MockAIClient(AIClient):
    """Mock AI client that returns pre-defined responses."""

    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate mock response based on prompt keywords."""
        prompt_lower = prompt.lower()

        # Idea Refinement (NEW - check this first!)
        if "refine" in prompt_lower and "original idea:" in prompt_lower:
            return self._mock_refine_idea(prompt)

        # Stage 1: Topic Curation
        if "curate" in prompt_lower or "topic" in prompt_lower:
            return self._mock_topic_curation()

        # Stage 2: Content Development
        elif "develop" in prompt_lower or "write content" in prompt_lower:
            if "bridge" in prompt_lower:
                return self._mock_bridge_content()
            elif "aspirational" in prompt_lower:
                return self._mock_aspirational_content()
            elif "current" in prompt_lower:
                return self._mock_current_content()
            return self._mock_bridge_content()

        # Stage 3: Platform Optimization
        elif "linkedin" in prompt_lower or "optimize" in prompt_lower:
            return self._mock_linkedin_post()
        elif "twitter" in prompt_lower or "thread" in prompt_lower:
            return self._mock_twitter_thread()

        # Default
        return "This is a mock AI response for demo purposes."

    def is_available(self) -> bool:
        """Mock client is always available."""
        return True

    def _mock_refine_idea(self, prompt: str) -> str:
        """Mock refinement that uses the actual user input."""
        # Extract the original idea from the prompt
        try:
            start_marker = "Original idea:"
            end_marker = "Please:"

            start_idx = prompt.find(start_marker)
            end_idx = prompt.find(end_marker)

            if start_idx != -1 and end_idx != -1:
                original_idea = prompt[start_idx + len(start_marker):end_idx].strip()
            else:
                return "Unable to refine: Could not parse your input."

            # Simple mock refinement: add structure and professional language
            lines = original_idea.split('\n')
            refined_parts = []

            # Add an engaging opening if the idea is short
            if len(original_idea) < 200:
                refined_parts.append(f"Here's an interesting perspective on this:\n")

            # Add the original content with slight enhancements
            for line in lines:
                if line.strip():
                    # Capitalize first letter if needed
                    refined_line = line.strip()
                    if refined_line and refined_line[0].islower():
                        refined_line = refined_line[0].upper() + refined_line[1:]
                    refined_parts.append(refined_line)

            # Add a call-to-action or closing thought
            if len(original_idea) > 50:
                refined_parts.append("\nThis could be valuable for professionals looking to improve their approach.")

            return "\n\n".join(refined_parts)

        except Exception:
            # Fallback if parsing fails
            return f"[Mock AI] Your idea has been refined with better structure, clarity, and professional tone. (Note: This is a mock AI client for demo purposes. Configure a real AI service in settings for actual refinement.)"

    def _mock_topic_curation(self) -> str:
        """Mock topic curation output."""
        return """
**Topic 1: The Power of Asynchronous Communication**

**Core Insight:** Remote teams struggle with communication overhead, leading to meeting fatigue and decreased productivity.

**Audience Resonance:** Many professionals are dealing with back-to-back meetings and feeling overwhelmed.

**Authentic Angle:** Personal experience implementing async-first communication in a distributed team.

**Potential Hook:** "We eliminated 70% of our meetings and productivity actually went up. Here's how..."

**Topic 2: Building Systems That Scale**

**Core Insight:** Manual processes become bottlenecks as teams grow.

**Audience Resonance:** Growing companies face operational chaos without proper systems.

**Authentic Angle:** Learned this lesson the hard way when our team doubled in size.

**Potential Hook:** "The moment I realized our success was becoming our biggest problem..."
"""

    def _mock_bridge_content(self) -> str:
        """Mock bridge content."""
        return """
**Title:** From Meeting Fatigue to Async Excellence

I used to think more meetings meant better communication.

Then our team grew from 5 to 15 people, and my calendar turned into a nightmare. Back-to-back video calls. No time for deep work. Everyone exhausted.

Sound familiar?

Here's what changed everything: We implemented async-first communication.

**The 3-Rule Framework:**

1. **Default to Writing** - If it doesn't need a live discussion, write it down
2. **Set Response SLAs** - 24 hours for non-urgent, 4 hours for important
3. **Document Everything** - Make information accessible, not locked in someone's head

**Results after 3 months:**
- 70% reduction in meetings
- 2x increase in deep work time
- Team satisfaction up 40%

The key insight: Synchronous time is precious. Use it only when async won't work.

**When to meet:**
- Complex decision-making
- Conflict resolution
- Team building
- Creative brainstorming

**When to use async:**
- Status updates
- Project progress
- FYIs and announcements
- Simple decisions

Start small. Pick one recurring meeting and replace it with a Loom video or written update. You'll be surprised how much time you get back.
"""

    def _mock_aspirational_content(self) -> str:
        """Mock aspirational content."""
        return """
**Title:** The Operational Framework for Scaling Remote Teams

A Harvard Business Review study found that companies lose an average of 31 hours per month per employee to unnecessary meetings. For a 50-person company, that's $104,000 in lost productivity monthly.

**The Async-First Operating System:**

**1. Communication Hierarchy**
- Tier 1: Documentation (Notion, Confluence)
- Tier 2: Async updates (Loom, Slack threads)
- Tier 3: Scheduled sync time (meetings)

**2. Decision-Making Framework**
- Type 1 decisions (reversible): Async approval with 24hr feedback window
- Type 2 decisions (high-impact): Synchronous discussion required

**3. Meeting Protocol**
- All meetings require pre-read materials
- 15min max for tactical syncs
- 60min max for strategic sessions
- Record and share for timezone flexibility

**Key Metrics to Track:**
- Meeting hours per employee per week
- Response time to async requests
- Documentation coverage percentage
- Employee deep work hours

**Implementation Roadmap:**

Week 1-2: Audit current meeting load
Week 3-4: Categorize meetings by necessity
Week 5-6: Replace 30% with async alternatives
Week 7-8: Train team on new protocols

Companies like GitLab and Zapier have proven async-first can work at scale. GitLab's 1,300+ employees across 65 countries operate almost entirely asynchronously.

The future of work isn't about where we work. It's about when we work together.
"""

    def _mock_current_content(self) -> str:
        """Mock current audience content."""
        return """
**Title:** I Accidentally Discovered the Secret to Better Work-Life Balance

Can I be honest with you?

Six months ago, I was drowning. Notifications every 30 seconds. Zoom calls overlapping. Messages at 10pm asking "quick questions."

I thought this was just the cost of being a good teammate.

Then something clicked during a particularly exhausting week where I realized I'd spent 32 hours in meetings but barely moved my projects forward.

**What I changed:**

I started treating my calendar like a finite resource. Because it is.

- Turned off all notifications except DMs from my boss
- Blocked 9-11am every day for deep work (no meetings allowed)
- Started using Loom for updates instead of scheduling calls
- Set an auto-responder: "I check messages at 9am, 1pm, and 4pm"

**What happened:**

People adapted. The world didn't end. And I got more done in a week than I had in the previous month.

The biggest surprise? My team actually preferred it. They had more clarity, fewer interruptions, and better documentation.

Here's what I learned: The "always available" culture isn't productive. It's performative.

Real productivity comes from focused, uninterrupted work. Not from instant responses.

If you're feeling overwhelmed, you don't need to work harder. You need to protect your time more fiercely.

What's one change you could make this week to reclaim your calendar?
"""

    def _mock_linkedin_post(self) -> str:
        """Mock LinkedIn post."""
        return """
I used to think more meetings meant better communication.

Then our team grew from 5 to 15 people, and my calendar turned into a nightmare.

Sound familiar?

Here's what changed everything: We implemented async-first communication.

The 3-Rule Framework:

→ Default to Writing
If it doesn't need live discussion, write it down

→ Set Response SLAs
24 hours for non-urgent, 4 hours for important

→ Document Everything
Make information accessible, not locked in heads

Results after 3 months:
• 70% reduction in meetings
• 2x increase in deep work time
• Team satisfaction up 40%

The key insight: Synchronous time is precious.

Use it only when async won't work.

When to meet:
• Complex decisions
• Conflict resolution
• Team building
• Creative brainstorming

When to use async:
• Status updates
• Project progress
• FYIs
• Simple decisions

Start small. Pick one recurring meeting and replace it with a Loom video or written update.

You'll be surprised how much time you get back.

What's one meeting you could eliminate this week?

#RemoteWork #Productivity #Leadership #AsyncFirst #TeamManagement
"""

    def _mock_twitter_thread(self) -> str:
        """Mock Twitter thread."""
        return """
THREAD: How we cut 70% of our meetings and increased productivity

1/ I used to think more meetings = better communication

Then our team grew from 5 to 15 people and my calendar became a nightmare

Here's what we did instead 👇

2/ We implemented an "async-first" communication model

The rule: If it doesn't require live discussion, write it down

Sounds simple. Changed everything.

3/ The 3-Rule Framework:

→ Default to writing
→ Set response SLAs (24hrs non-urgent)
→ Document everything

Made information accessible, not locked in someone's head

4/ Results after 3 months:

• 70% fewer meetings
• 2x more deep work time
• Team satisfaction up 40%

And get this: people actually preferred it

5/ When TO meet:

• Complex decisions
• Conflict resolution
• Team building
• Creative brainstorms

When NOT to meet:

• Status updates
• FYIs
• Project progress
• Simple decisions

6/ Start small this week:

Pick ONE recurring meeting

Replace it with:
- A Loom video, or
- A written update, or
- A Slack thread

Watch what happens

7/ Synchronous time is precious

Use it only when async won't work

The "always available" culture isn't productive

It's performative

Real work happens in focused, uninterrupted blocks

8/ What's one meeting you could eliminate this week?

Reply and let me know 👇
"""
