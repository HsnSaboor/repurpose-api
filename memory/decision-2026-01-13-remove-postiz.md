# Decision: Remove Auto-Posting Features (Postiz Integration)

**Date:** January 13, 2026  
**Decision By:** User Request  
**Status:** Implemented

---

## Context

The project initially included a Postiz integration for auto-posting generated content to social media platforms (X/Twitter, Instagram, LinkedIn, YouTube, etc.). During testing, we discovered:

1. **X API Free Tier Credits Depleted** - X has effectively killed their free tier with the Pay-Per-Use model (October 2025)
2. **Complex API Requirements** - Each platform requires app review, business verification, and ongoing maintenance
3. **Focus Shift** - User wants to focus on **content generation only**, not distribution

## Decision

**Remove all auto-posting/publishing features** and focus the project solely on content generation.

## What Was Removed

### Specs
- `specs/postiz-integration.md` - Deleted
- `specs/features.md` - Removed Postiz section
- `specs/specs.md` - Removed Postiz reference

### Tasks
- `tasks/postiz-integration.md` - Deleted (24 atomic tasks)
- `tasks/tasks.md` - Removed entire Postiz Epic (POSTIZ-001 to POSTIZ-016)

### Backlog Items Removed
- Postiz image generation for carousel slides
- Postiz video upload support
- Postiz analytics integration
- Postiz webhook support for post status updates

## What Remains (Content Generation Focus)

### Core Features
- YouTube video → content generation
- Document → content generation  
- URL → content generation (via trafilatura)
- Brain knowledge base system
- Vision-based generation
- Full AI mode generation
- Hybrid source selection

### Content Types Generated
- Instagram Reels (script, hook, caption)
- Image Carousels (4-8 slides)
- Tweets (280 char limit, optional thread)

## Code Files Removed

The following implementation files were deleted:
- `api/routers/postiz.py` - API router
- `core/services/postiz_service.py` - Postiz API client
- `core/services/postiz_content_mapper.py` - Content mapping
- `tests/test_postiz.py` - Unit tests

The following code sections were removed:
- `main.py` - Removed Postiz router import/include
- `api/models.py` - Removed all Postiz models (~170 lines)
- `core/database.py` - Removed PostizPost table model

**Verification:** App loads successfully with no Postiz routes.

## Rationale

1. **Simpler Scope** - Content generation is the core value; publishing is a separate concern
2. **Platform Independence** - Users can copy/paste or use their preferred publishing tool
3. **No API Costs** - Avoid X API credits, Meta app review, etc.
4. **Faster Development** - Focus resources on improving content quality

## Alternative Considered

**Mixpost Integration** - Self-hosted social media scheduler with:
- One-time $299 (Pro) or $1,199 (Enterprise/SaaS) pricing
- Better Meta app review documentation
- White-label SaaS option

**Decision:** Defer to user's future discretion. Not implementing now.
