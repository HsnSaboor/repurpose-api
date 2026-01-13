# Task Tracker

## Status Legend
- `[ ]` Todo - Not started
- `[·]` Active - In progress
- `[X]` Done - Completed and verified
- `[?]` Blocked - Waiting on dependency

---

## Epic: Brain Knowledge Base System (v2.0)

### Phase 1: Database & Models

- [X] **BRAIN-001**: Create `brain_sources` table in database.py
  - Add BrainSource SQLAlchemy model
  - Fields: source_id, source_type, title, content, summary, topics, tags, source_metadata, embedding, timestamps
  - Add indexes for source_type and last_used_at

- [X] **BRAIN-002**: Create `brain_sessions` table in database.py
  - Add BrainSession SQLAlchemy model
  - Fields: session_id, mode, user_vision, selected_source_ids, matched_source_ids, generated_content, status
  - Track generation sessions for both vision and auto modes

- [X] **BRAIN-003**: Update Videos table with Brain indexing fields
  - Add: is_indexed, indexed_at, source_type, tags, topics, summary, embedding_id
  - Create migration-safe column additions
  - Migration script: utilities/migrate_brain_fields.py

- [X] **BRAIN-004**: Create Pydantic models for Brain API
  - BrainSource, BrainSourceCreate, BrainSourceUpdate
  - VisionGenerateRequest, AutoGenerateRequest
  - BrainSearchRequest, BrainSearchResponse
  - Add to api/models.py

### Phase 2: Core Brain Service

- [X] **BRAIN-005**: Create brain_service.py in core/services/
  - BrainService class with CRUD operations
  - index_source() - Extract topics, generate summary, create embedding
  - search_sources() - Semantic search implementation
  - get_relevant_sources() - Match sources to user vision

- [X] **BRAIN-006**: Implement source indexing logic (included in BRAIN-005)
  - Auto-extract topics from content using LLM
  - Generate 200-500 char summary
  - Store embedding for semantic search (simple text similarity initially)

- [X] **BRAIN-007**: Implement semantic search (included in BRAIN-005)
  - Text-based similarity search (cosine similarity on TF-IDF or embeddings)
  - Filter by source_type, min_score
  - Return ranked results with snippets

### Phase 3: Generation Modes

- [X] **BRAIN-008**: Implement Vision-Based Generation (in brain_content_generator.py)
  - Accept user vision/idea text
  - Search Brain for matching sources
  - Combine user vision + matched source content
  - Generate content that reflects user's intent backed by source data
  - Return matched sources with scores + generated content

- [X] **BRAIN-009**: Implement Full AI Mode - Single (in brain_content_generator.py)
  - Accept selected source_ids
  - Analyze sources and generate 1 optimal content piece
  - Choose best content type based on source content

- [X] **BRAIN-010**: Implement Full AI Mode - Multiple (in brain_content_generator.py)
  - Accept selected source_ids + count
  - Generate exactly N content pieces
  - Distribute across requested content types

- [X] **BRAIN-011**: Implement Full AI Mode - Auto (in brain_content_generator.py)
  - Accept selected source_ids
  - AI determines optimal number of pieces based on source richness
  - Generate and return with explanation of count decision

- [X] **BRAIN-012**: Implement Hybrid Source Selection Mode (in brain_content_generator.py)
  - Accept user_source_ids + ai_augment config
  - Strategy: `augment` - AI adds related sources based on hint
  - Strategy: `fill` - AI fills to reach target source count
  - Strategy: `support` - AI sources used for context only
  - Combine user + AI sources for content generation
  - Track primary vs supporting source attribution in output

### Phase 4: API Endpoints

- [X] **BRAIN-013**: Create brain router (api/routers/brain.py)
  - Register with FastAPI app
  - Set up /brain/* route prefix

- [X] **BRAIN-014**: Implement Brain Source CRUD endpoints
  - GET /brain/sources/ - List with pagination, filtering
  - GET /brain/sources/{source_id} - Get single source
  - POST /brain/sources/ - Add source (YouTube, document, or raw text)
  - PATCH /brain/sources/{source_id} - Update tags/topics
  - DELETE /brain/sources/{source_id} - Remove source

- [X] **BRAIN-015**: Implement Brain Generation endpoints
  - POST /brain/generate/vision - Vision-based generation
  - POST /brain/generate/auto - Full AI mode (single/multiple/auto)
  - POST /brain/generate/hybrid - Hybrid source selection

- [X] **BRAIN-016**: Implement Brain Search endpoint
  - POST /brain/search - Semantic search with filters

### Phase 5: Integration & Auto-Indexing

- [X] **BRAIN-017**: Auto-index on video/document processing
  - Hook into /process-video/ and /process-video-stream/
  - After successful processing, auto-add to Brain
  - Extract topics and summary asynchronously

- [X] **BRAIN-018**: Backfill existing videos into Brain
  - Create utility script to index existing videos table
  - Generate topics/summaries for historical data
  - Script: utilities/backfill_brain.py

### Phase 6: CLI Integration

- [X] **BRAIN-019**: Add Brain commands to CLI
  - `--brain-list` - List sources in Brain
  - `--brain-search "query"` - Search Brain
  - `--from-brain source_id1,source_id2` - Generate from Brain sources
  - `--vision "idea"` - Vision-based generation from CLI
  - `--brain-stats` - Show Brain knowledge base statistics

---

## Epic: URL-to-Markdown Source Support

### Phase 1: Core Infrastructure

- [X] **URL-001**: Add trafilatura dependency
  - Add `trafilatura>=2.0.0` to requirements.txt
  - Verify installation works

- [X] **URL-002**: Create URLExtractor service
  - Create `core/services/url_service.py`
  - Implement `extract_from_url(url)` method
  - Return content (markdown), title, metadata
  - Handle fetch failures, empty content errors

- [X] **URL-003**: Add Pydantic models for URL sources
  - Add `URLSourceCreate` model in `api/models.py`
  - Include: url, title (optional), tags, extract_options
  - Add `URLExtractOptions` model (include_tables, include_links, include_images)

### Phase 2: API Integration

- [X] **URL-004**: Update Brain router for URL sources
  - Modify `POST /brain/sources` to accept `source_type: "url"`
  - Extract content using URLExtractor
  - Auto-extract title from metadata if not provided
  - Store original_url in source_metadata

- [X] **URL-005**: Add URL validation
  - Validate URL format
  - Block YouTube URLs (use video processing instead)
  - Block localhost/private IPs
  - Handle redirects

### Phase 3: CLI Integration

- [X] **URL-006**: Add `--add-url` CLI flag
  - Add argument to repurpose.py
  - Extract content and add to Brain
  - Show extraction summary (title, word count, topics)

- [X] **URL-007**: Auto-detect URL input in CLI
  - In `parse_input_source()`, detect non-YouTube URLs
  - Process as URL source type
  - Skip if URL looks like YouTube

### Phase 4: Testing & Polish

- [X] **URL-008**: Create verification tests
  - Test extraction from sample URLs
  - Test error handling (404, blocked, empty)
  - Test metadata extraction

- [X] **URL-009**: Update documentation
  - Add URL examples to CLI help
  - Update API docs with URL examples
  - Add troubleshooting section

---

## URL Feature Complete!

---

## Backlog (Future)

- [ ] Add vector embeddings using sentence-transformers
- [ ] Brain analytics dashboard
- [ ] Cross-source content synthesis
- [ ] Source clustering and topic graphs
