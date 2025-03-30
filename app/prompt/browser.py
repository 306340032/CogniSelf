
NEXT_STEP_PROMPT = """
What should I do next to achieve my goal?

When you see [Current state starts here], focus on the following:
- Current URL and page title{url_placeholder}
- Available tabs{tabs_placeholder}
- Interactive elements and their indices
- Content above{content_above_placeholder} or below{content_below_placeholder} the viewport (if indicated)
- Any action results or errors{results_placeholder}

For browser interactions:
- To navigate: browser_use with action="go_to_url", url="..."
- To click: browser_use with action="click_element", index=N
- To type: browser_use with action="input_text", index=N, text="..."
- To extract: browser_use with action="extract_content", goal="..."
- To scroll: browser_use with action="scroll_down" or "scroll_up"

Consider both what's visible and what might be beyond the current viewport.
Be methodical - remember your progress and what you've learned so far.
"""