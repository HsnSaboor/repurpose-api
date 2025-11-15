# Video Processing Flow

## Detailed Video Processing Architecture & User Flow

---

## High-Level Processing Flow

```mermaid
graph TB
    subgraph "User Interface"
        A[User Enters URL] --> B[Frontend Validation]
        B --> C[Fetch Video Info]
    end
    
    subgraph "Backend Processing"
        C --> D{Video Info Valid?}
        D -->|No| E[Return Error]
        D -->|Yes| F[Show Video Preview]
        
        F --> G[User Configures Style]
        G --> H[User Clicks Generate]
        H --> I[API: POST /process-video]
        
        I --> J{Check Cache}
        J -->|Exists & !Force| K[Return Cached]
        J -->|New/Force| L[Start Processing]
        
        L --> M[Fetch Transcript]
        M --> N{Transcript Available?}
        N -->|No| O[Error: No Transcript]
        N -->|Yes| P[Analyze Content]
        
        P --> Q[Generate Ideas with AI]
        Q --> R[Validate Ideas]
        R --> S{Valid?}
        S -->|No| T[Retry Generation]
        T --> Q
        S -->|Yes| U[Generate Content Pieces]
        
        U --> V[Validate Content]
        V --> W{All Valid?}
        W -->|No| X[Fix Validation Errors]
        X --> U
        W -->|Yes| Y[Save to Database]
    end
    
    subgraph "Response"
        Y --> Z[Return Content]
        K --> Z
        O --> AA[Return Error]
        E --> AA
        
        Z --> AB[Show Success Screen]
        AA --> AC[Show Error Screen]
    end
```

---

## Detailed Step-by-Step Flow

### Step 1: URL Input & Validation

```mermaid
sequenceDiagram
    actor User
    participant UI
    participant Frontend
    participant Backend
    participant YouTube
    
    User->>UI: Paste YouTube URL
    UI->>Frontend: Validate URL format
    
    alt Invalid Format
        Frontend->>UI: Show inline error
        UI->>User: "Invalid YouTube URL"
    else Valid Format
        UI->>User: Show checkmark
        UI->>User: Enable "Fetch Info"
    end
    
    User->>UI: Click "Fetch Video Info"
    UI->>Frontend: Extract video ID
    Frontend->>Backend: GET /video-info?video_id=xyz
    Backend->>YouTube: Fetch video metadata
    
    alt Video Not Found
        YouTube->>Backend: 404 Error
        Backend->>Frontend: Error response
        Frontend->>UI: Show error message
        UI->>User: "Video not found"
    else Video Found
        YouTube->>Backend: Video data
        Backend->>Frontend: Video metadata
        Frontend->>UI: Display preview
        UI->>User: Show thumbnail, title, etc.
    end
```

---

### Step 2: Style Selection & Configuration

```mermaid
graph TD
    A[Video Preview Shown] --> B{Style Selection}
    
    B -->|Default| C[Use Pre-selected Preset]
    B -->|Choose Preset| D[Select from Dropdown]
    B -->|Custom| E[Expand Custom Form]
    
    C --> F[Display Preset Details]
    D --> F
    E --> G[Fill Custom Fields]
    G --> H[Validate Custom Input]
    H --> I{Valid?}
    I -->|No| J[Show Errors]
    J --> G
    I -->|Yes| F
    
    F --> K{Advanced Options?}
    K -->|No| L[Use Defaults]
    K -->|Yes| M[Configure Field Limits]
    M --> N[Set Idea Ranges]
    N --> L
    
    L --> O[Enable Generate Button]
```

---

### Step 3: Content Generation Process

```mermaid
sequenceDiagram
    actor User
    participant UI
    participant Frontend
    participant Backend
    participant AI Service
    participant Database
    
    User->>UI: Click "Generate Content"
    UI->>Frontend: Submit form
    Frontend->>Backend: POST /process-video
    
    Backend->>Database: Check if exists
    
    alt Already Exists
        Database->>Backend: Return existing
        Backend->>Frontend: Cached content
        Frontend->>UI: Show results
    else New or Force Regenerate
        Backend->>Backend: Fetch transcript
        Note over Backend: YouTube Transcript API
        
        Backend->>AI Service: Generate ideas (LLM)
        activate AI Service
        AI Service->>AI Service: Analyze transcript
        AI Service->>AI Service: Generate 6-8 ideas
        AI Service->>Backend: Return ideas
        deactivate AI Service
        
        Backend->>Backend: Validate ideas
        
        loop For each idea
            Backend->>AI Service: Generate content pieces
            activate AI Service
            Note over AI Service: Generate Reel, Carousel, Tweet
            AI Service->>Backend: Content pieces
            deactivate AI Service
            
            Backend->>Backend: Validate each piece
            
            alt Validation Failed
                Backend->>AI Service: Retry with fixes
                activate AI Service
                AI Service->>Backend: Fixed content
                deactivate AI Service
            end
        end
        
        Backend->>Database: Save all content
        Database->>Backend: Confirm saved
        Backend->>Frontend: Return content
        Frontend->>UI: Display results
    end
    
    UI->>User: Show success + content
```

---

### Step 4: Real-time Progress Updates

```mermaid
sequenceDiagram
    participant UI
    participant Frontend
    participant Backend
    participant WebSocket
    
    Frontend->>Backend: POST /process-video (async)
    Backend->>Frontend: Return job_id
    
    Frontend->>WebSocket: Connect to job updates
    
    loop Processing
        Backend->>WebSocket: Progress update
        WebSocket->>Frontend: Status message
        Frontend->>UI: Update progress bar
        UI->>User: Visual feedback
        
        Note over Backend,WebSocket: Steps:<br/>1. Fetching transcript<br/>2. Analyzing content<br/>3. Generating ideas<br/>4. Creating content
    end
    
    Backend->>WebSocket: Complete message
    WebSocket->>Frontend: Final status
    Frontend->>Backend: GET /content/{video_id}
    Backend->>Frontend: Full content
    Frontend->>UI: Render results
```

---

## State Machine: Processing States

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Validating: Submit URL
    Validating --> Invalid: Validation Fails
    Validating --> Ready: Validation Passes
    
    Invalid --> Idle: Fix Input
    
    Ready --> Fetching: Click Generate
    Fetching --> FetchError: Network Error
    Fetching --> Transcribing: Info Retrieved
    
    FetchError --> Ready: Retry
    
    Transcribing --> TranscriptError: Not Available
    Transcribing --> Analyzing: Transcript OK
    
    TranscriptError --> [*]: User Cancels
    TranscriptError --> Ready: Try Different Video
    
    Analyzing --> GeneratingIdeas: Analysis Complete
    GeneratingIdeas --> GeneratingContent: Ideas Ready
    GeneratingContent --> Validating: Content Created
    
    Validating --> Retrying: Validation Fails
    Retrying --> GeneratingContent: Fix & Retry
    Validating --> Saving: All Valid
    
    Saving --> Complete: Success
    Saving --> SaveError: DB Error
    
    SaveError --> Retrying: Retry Save
    
    Complete --> [*]
    
    note right of Complete: Show success screen<br/>with all content
```

---

## Error Handling Flow

```mermaid
graph TD
    A[Error Occurs] --> B{Error Type?}
    
    B -->|Network Error| C[Show Retry]
    C --> D{User Retries?}
    D -->|Yes| E[Attempt Again]
    D -->|No| F[Return to Input]
    
    B -->|Transcript Unavailable| G[Show Error Message]
    G --> H[Suggest: Try different video]
    H --> F
    
    B -->|Rate Limit| I[Show Wait Timer]
    I --> J[Countdown Display]
    J --> K{Time Elapsed?}
    K -->|No| J
    K -->|Yes| L[Enable Retry]
    
    B -->|Validation Error| M[Show Validation Issues]
    M --> N[Auto-retry with fixes]
    N --> O{Retry Count < 3?}
    O -->|Yes| P[Generate Again]
    O -->|No| Q[Manual Intervention]
    Q --> R[Contact Support]
    
    B -->|API Key Invalid| S[Navigate to Settings]
    S --> T[Update API Key]
    T --> U[Test Connection]
    U --> V{Valid?}
    V -->|Yes| E
    V -->|No| T
    
    E --> W[Resume Processing]
```

---

## Optimization: Caching Strategy

```mermaid
graph LR
    A[Request Content] --> B{Check Cache}
    
    B -->|Cache Hit| C[Return Immediately]
    B -->|Cache Miss| D[Generate Content]
    
    D --> E[Save to Cache]
    E --> F[Return Content]
    
    G[Force Regenerate?] -->|Yes| D
    G -->|No| B
    
    H[Cache Expiry] -.-> I[Remove from Cache]
    I -.-> D
    
    C --> J[Serve to User]
    F --> J
```

---

## Content Validation Flow

```mermaid
graph TD
    A[Generated Content] --> B[Validate Structure]
    B --> C{Has Required Fields?}
    C -->|No| D[Log Missing Fields]
    D --> E[Retry Generation]
    C -->|Yes| F[Validate Lengths]
    
    F --> G{Within Limits?}
    G -->|No| H[Truncate or Regenerate]
    H --> E
    G -->|Yes| I[Validate Format]
    
    I --> J{Proper Format?}
    J -->|No| K[Fix Formatting]
    K --> L{Auto-fixable?}
    L -->|Yes| M[Apply Fixes]
    L -->|No| E
    J -->|Yes| M
    
    M --> N[Content Valid]
    N --> O[Save to Database]
    
    E --> P{Retry Count < 3?}
    P -->|Yes| A
    P -->|No| Q[Return Error]
```

---

## Concurrent Processing (Bulk)

```mermaid
graph TB
    A[Bulk Request] --> B[Parse Video List]
    B --> C[Create Processing Queue]
    
    C --> D{Processing Strategy}
    D -->|Sequential| E[Process One by One]
    D -->|Parallel| F[Process in Batches]
    
    E --> G[Video 1]
    G --> H[Video 2]
    H --> I[Video 3]
    I --> J[...]
    
    F --> K[Batch 1: Videos 1-3]
    F --> L[Batch 2: Videos 4-6]
    F --> M[Batch 3: Videos 7-9]
    
    K --> N[Wait for Batch]
    L --> N
    M --> N
    
    J --> O[Collect Results]
    N --> O
    
    O --> P{All Successful?}
    P -->|Yes| Q[Return All]
    P -->|Partial| R[Return Success + Errors]
    P -->|All Failed| S[Return Errors]
    
    Q --> T[Show Success Screen]
    R --> U[Show Partial Success]
    S --> V[Show Error Screen]
```

---

## Performance Monitoring

```mermaid
graph LR
    A[Start Processing] --> B[Log Start Time]
    B --> C[Execute Steps]
    C --> D[Log Each Step Duration]
    D --> E[Calculate Total Time]
    E --> F[Save Metrics]
    
    F --> G{Time > Threshold?}
    G -->|Yes| H[Alert Slow Processing]
    G -->|No| I[Normal Flow]
    
    H --> J[Investigate]
    J --> K{Issue Found?}
    K -->|Yes| L[Optimize]
    K -->|No| M[Acceptable]
    
    I --> N[Continue]
    M --> N
    L --> N
```

---

## Key Timing Expectations

| Step | Expected Duration | Timeout |
|------|------------------|---------|
| Fetch Video Info | 1-2s | 10s |
| Fetch Transcript | 2-5s | 15s |
| Generate Ideas (AI) | 10-20s | 60s |
| Generate Content (AI per piece) | 5-15s | 45s |
| Validate & Save | 1-2s | 10s |
| **Total** | **30-90s** | **180s** |

---

## API Endpoints Involved

```
GET  /video-info?video_id={id}
POST /process-video
  Body: {
    video_id: string
    style_preset?: string
    custom_style?: object
    force_regenerate?: boolean
  }
  
GET  /processing-status/{video_id}
  Response: {
    status: "queued" | "processing" | "complete" | "failed"
    progress: number (0-100)
    current_step: string
    estimated_time_remaining: number
  }
  
GET  /content/by-video/{video_id}
  Response: {
    content_pieces: ContentPiece[]
  }
  
POST /edit-content
  Body: {
    video_id: string
    content_piece_id: string
    edit_prompt: string
    content_type: string
  }
```

---

## Notes on Implementation

### Frontend Responsibilities:
- URL validation
- Form state management
- Progress tracking
- Error display
- Result rendering

### Backend Responsibilities:
- Video metadata fetching
- Transcript extraction
- AI content generation
- Validation & retry logic
- Database operations
- Caching

### Best Practices:
1. Always validate user input
2. Provide real-time feedback
3. Handle errors gracefully
4. Cache aggressively
5. Retry failed operations (with limits)
6. Monitor performance
7. Log everything for debugging
8. Use timeouts to prevent hangs
