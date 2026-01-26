# Content Management Guide
**LinkedIn Content Pipeline**

---

## 🎯 Overview

You now have complete control over your ideas and generated content. This guide shows you how to manage, reuse, combine, and delete content entries.

---

## 💡 Managing Ideas

### Adding Ideas

**Two Entry Modes:**

1. **Quick Idea** (Default)
   - Short observations (150px height)
   - Quick thoughts and insights
   - Example: "Noticed team productivity increased with async communication"

2. **Journal Entry** (New!)
   - Longer reflections (400px height)
   - Full stories with context
   - Include emotions, lessons learned, what you'd do differently
   - Example: Full story about implementing a new team process

### Editing Ideas

1. Go to "💡 Add Ideas"
2. Find your idea in the list below
3. Click **"Edit"** button
4. Modify text or category
5. Click **"Save"** or **"Cancel"**

### Deleting Ideas

1. Find the idea you want to remove
2. Click **"Delete"** button
3. Idea is permanently removed
4. Page refreshes automatically

### Filtering Ideas

- **Show used ideas**: Toggle to see ideas already used in content
- **Filter by category**: View only specific categories
- **Sort by**: Newest or oldest first

---

## 📄 Managing Generated Content

### View All Content

1. Go to "📄 Review Content"
2. In sidebar, select **"All Content"** view
3. See list of all generated content

### Actions Per Content Item:

#### 👁️ View
- Click to see detailed view
- Shows topics, content, and platform posts
- Navigate tabs for different content types

#### 📥 Export
**Three formats available:**

1. **Text (.txt)**
   - Plain text format
   - Easy to read
   - Compatible everywhere

2. **Markdown (.md)**
   - Formatted with headers
   - GitHub-ready
   - Great for documentation

3. **JSON (.json)**
   - Complete data export
   - Includes all metadata
   - For backup or processing

#### 📋 Copy All Posts
- Combines all LinkedIn and Twitter posts
- Displays in code block for easy copying
- Separated by platform
- Each post numbered

#### 🗑️ Delete
- Removes content permanently
- Click once to delete
- Page refreshes automatically

---

## 🔄 Reusing Content

### Combining Multiple Posts

**Method 1: Manual Combination**
1. Go to "📄 Review Content"
2. Open first content item
3. Click "📋 Copy All Posts"
4. Copy the text
5. Repeat for other content items
6. Paste all into your editor
7. Edit and combine as needed

**Method 2: Export and Merge**
1. Export multiple content items as Markdown
2. Open files in text editor
3. Copy/paste sections you want
4. Create new combined document

### Repurposing Ideas

**Option 1: Mark as Unused**
1. Ideas are marked "used" after pipeline runs
2. To reuse: currently need to edit the data file manually
3. *Future feature: "Mark as Unused" button*

**Option 2: Create New Idea from Old**
1. View old idea
2. Copy the text
3. Create new idea with modifications
4. Original remains marked as "used"

---

## 🗂️ Content Organization Tips

### For Ideas:

1. **Use Categories Effectively**
   - Leadership: Team management, decision-making
   - Personal Growth: Lessons learned, habits
   - AI & Technology: Tools, automation
   - etc.

2. **Add Context in Journal Mode**
   - Tell full stories
   - Include what happened before/after
   - Explain your thought process
   - Add emotional context

3. **Track Sources**
   - Note where ideas came from
   - Meeting notes, books, conversations
   - Helps you remember context

### For Generated Content:

1. **Review Regularly**
   - Check "📄 Review Content" weekly
   - Delete outdated content
   - Export valuable pieces

2. **Export Important Content**
   - Save successful posts
   - Keep as templates
   - Build content library

3. **Organize by Campaign**
   - Use profile_id to group related content
   - Export all content for a campaign
   - Combine into master document

---

## 📊 Workflow Examples

### Weekly Content Creation

1. **Monday**: Add 10+ ideas from journal entries
2. **Tuesday**: Run pipeline, generate content
3. **Wednesday**: Review in "📄 Review Content"
4. **Thursday**: Copy posts, schedule on platforms
5. **Friday**: Export successful content for library

### Content Repurposing

1. Find high-performing content in "📄 Review Content"
2. Click "📥 Export" → Markdown
3. Edit for different audience/platform
4. Create new idea based on edited version
5. Run through pipeline again
6. Compare old vs new versions

### Building Content Library

1. **Monthly**: Review all generated content
2. Export best pieces as Markdown
3. Create folder structure:
   ```
   content-library/
   ├── leadership/
   ├── productivity/
   ├── tech/
   └── personal/
   ```
4. Tag by performance/topic
5. Reference when creating new content

---

## 🚀 Pro Tips

### Ideas Management

✅ **DO:**
- Add ideas immediately when you think of them
- Use journal mode for stories and experiences
- Include specific examples and numbers
- Categorize consistently
- Review unused ideas before running pipeline

❌ **DON'T:**
- Wait until you have "perfect" ideas
- Delete ideas too quickly (they might be useful later)
- Use overly generic descriptions
- Mix multiple unrelated ideas in one entry

### Content Management

✅ **DO:**
- Export content before deleting
- Review generated content within 24 hours
- Keep successful templates
- Combine related posts for campaigns
- Track what performs well

❌ **DON'T:**
- Delete all content at once (lose valuable data)
- Let content pile up without review
- Ignore the export feature
- Forget to organize by topic/campaign

---

## 🔧 Quick Reference

### Keyboard Shortcuts
*Note: These are browser standard shortcuts*
- `Ctrl/Cmd + F`: Find text on page
- `Ctrl/Cmd + C`: Copy selected text
- `Ctrl/Cmd + A`: Select all in text area

### File Locations
- Ideas: `data/ideas.json`
- Content: `data/generated_content.json`
- Profiles: `data/brand_profiles.json`

### API Rate Limits
- Gemini: 60 requests/minute
- Built-in rate limiting prevents quota issues
- Pipeline automatically retries on failure

---

## ❓ FAQs

**Q: Can I bulk delete ideas?**
A: Not currently. Delete individually or edit `data/ideas.json` directly.

**Q: Can I import ideas from a file?**
A: Yes! Add them to `data/ideas.json` following the format.

**Q: How do I backup my content?**
A: Copy the entire `data/` folder. Or export all content as JSON.

**Q: Can I undo a delete?**
A: No. Always export before deleting important content.

**Q: What's the max idea length?**
A: 5,000 characters (input sanitization limit).

**Q: Can I combine posts from different content items?**
A: Yes! Use "Copy All Posts" on each, then manually combine.

---

## 🆘 Troubleshooting

**Ideas not showing up?**
- Check filters (Show used ideas, Category filter)
- Verify ideas exist in `data/ideas.json`
- Refresh page

**Can't delete content?**
- Check file permissions on `data/` folder
- Try restarting the app
- Verify storage is working

**Export not working?**
- Check browser download settings
- Try different export format
- Ensure content has data to export

---

## 📝 Future Features

Coming soon:
- Bulk delete/export
- Mark content as "unused" to rerun
- Combine multiple content items in UI
- Content versioning
- Performance tracking integration
- Import/export ideas in bulk

---

**Need help?** Check the main README.md or create an issue on GitHub.
