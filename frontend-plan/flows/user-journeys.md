# User Journey Flowcharts

## Overview
Visual representations of key user journeys through the application using Mermaid diagrams.

---

## Journey 1: First-Time User - Single Video Processing

```mermaid
graph TD
    A[Land on Login Page] --> B[Create Account]
    B --> C[Verify Email Optional]
    C --> D[Arrive at Dashboard]
    D --> E{What to do?}
    E -->|See Quick Action| F[Click Process Video]
    E -->|See Navigation| G[Click Dashboard Nav]
    G --> F
    
    F[Navigate to Video Input] --> H[Paste YouTube URL]
    H --> I[Click Fetch Video Info]
    I --> J{Video Valid?}
    J -->|No| K[Show Error]
    K --> H
    J -->|Yes| L[See Video Preview]
    
    L --> M[Review Default Style]
    M --> N{Customize?}
    N -->|No| O[Click Generate Content]
    N -->|Yes| P[Adjust Style Settings]
    P --> O
    
    O --> Q[Watch Processing Status]
    Q --> R[Processing Complete]
    R --> S[View Generated Content]
    
    S --> T{Next Action?}
    T -->|Copy Content| U[Click Copy Button]
    U --> V[Success Toast]
    T -->|Edit Content| W[Open Editor]
    W --> X[Make Changes]
    X --> Y[Save Changes]
    T -->|Process More| F
    T -->|View All| Z[Go to Library]
```

---

## Journey 2: Returning User - Quick Content Generation

```mermaid
graph TD
    A[Login] --> B[Dashboard]
    B --> C[Click + New Button]
    C --> D[Enter Video URL]
    D --> E[Fetch Info]
    E --> F[Accept Default Style]
    F --> G[Generate]
    G --> H[View Results]
    H --> I{Satisfied?}
    I -->|Yes| J[Copy & Use]
    I -->|No| K[Quick AI Edit]
    K --> L[Make it more engaging]
    L --> M[Apply Edit]
    M --> N[Review Changes]
    N --> I
```

---

## Journey 3: Power User - Bulk Processing

```mermaid
graph TD
    A[Dashboard] --> B[Click Bulk Processing]
    B --> C[Choose Input Method]
    C --> D{Which Method?}
    
    D -->|Paste URLs| E[Enter Multiple URLs]
    D -->|Upload File| F[Upload TXT/CSV]
    D -->|From Channel| G[Enter Channel ID]
    
    E --> H[Parse Videos]
    F --> H
    G --> I[Fetch Channel Videos]
    I --> H
    
    H --> J[Review Queue]
    J --> K{Reorder/Remove?}
    K -->|Yes| L[Adjust Queue]
    L --> J
    K -->|No| M[Select Style]
    
    M --> N{Same Style All?}
    N -->|Yes| O[Choose One Preset]
    N -->|No| P[Set Style Per Video]
    
    O --> Q[Start Processing]
    P --> Q
    
    Q --> R[Monitor Progress]
    R --> S{All Complete?}
    S -->|No| R
    S -->|Yes| T[Review Results]
    
    T --> U{Any Errors?}
    U -->|Yes| V[Retry Failed]
    V --> R
    U -->|No| W[Export All]
    W --> X[Download Content]
```

---

## Journey 4: Content Editor - Refining Content

```mermaid
graph TD
    A[Content Library] --> B[Browse Content]
    B --> C[Find Content to Edit]
    C --> D[Click Edit Button]
    D --> E[Editor Opens]
    
    E --> F{Editing Method?}
    
    F -->|AI Edit| G[Type Prompt]
    G --> H[Make it more professional]
    H --> I[Apply AI Edit]
    I --> J[Preview Updates]
    
    F -->|Manual Edit| K[Switch to Manual Tab]
    K --> L[Edit Fields Directly]
    L --> J
    
    J --> M{Satisfied?}
    M -->|No| N{Try Again?}
    N -->|AI| G
    N -->|Manual| L
    M -->|Yes| O[Save Changes]
    
    O --> P[Success Toast]
    P --> Q{Next Action?}
    Q -->|Copy| R[Copy Content]
    Q -->|Edit Another| C
    Q -->|Done| S[Back to Library]
```

---

## Journey 5: Settings Configuration

```mermaid
graph TD
    A[Dashboard] --> B[Click Settings]
    B --> C[Settings Page Loads]
    C --> D{Which Section?}
    
    D -->|Account| E[Update Profile]
    E --> F[Save Changes]
    
    D -->|Content Config| G[Adjust Limits]
    G --> H[Min/Max Ideas]
    H --> I[Character Limits]
    I --> F
    
    D -->|API Keys| J[Enter API Key]
    J --> K[Test Connection]
    K --> L{Valid?}
    L -->|No| M[Show Error]
    M --> J
    L -->|Yes| N[Save Key]
    
    D -->|Style Presets| O[View Presets]
    O --> P{Action?}
    P -->|Create| Q[New Preset Modal]
    Q --> R[Fill Form]
    R --> S[Save Preset]
    P -->|Edit| T[Edit Preset Modal]
    T --> R
    P -->|Delete| U[Confirm Delete]
    U --> V[Remove Preset]
    
    F --> W[Success Message]
    N --> W
    S --> W
    V --> W
    W --> X[Continue Using App]
```

---

## Journey 6: Error Recovery

```mermaid
graph TD
    A[Processing Video] --> B{Success?}
    
    B -->|Yes| C[Show Content]
    
    B -->|No| D[Show Error]
    D --> E{Error Type?}
    
    E -->|Transcript Unavailable| F[Suggest Manual Upload]
    F --> G{User Action?}
    G -->|Upload| H[Upload Transcript Feature]
    G -->|Cancel| I[Return to Input]
    
    E -->|Invalid URL| J[Show URL Error]
    J --> K[Re-enter URL]
    K --> A
    
    E -->|Rate Limit| L[Show Wait Time]
    L --> M[Wait or Schedule]
    M --> N{Schedule?}
    N -->|Yes| O[Add to Queue]
    N -->|No| P[Wait Then Retry]
    P --> A
    
    E -->|API Error| Q[Show Error Message]
    Q --> R{Retry?}
    R -->|Yes| A
    R -->|No| S[Contact Support]
```

---

## Journey 7: Mobile User - Quick Copy Workflow

```mermaid
graph TD
    A[Open App on Mobile] --> B[Login]
    B --> C[Dashboard]
    C --> D[Tap + FAB]
    D --> E[Video Input Sheet]
    E --> F[Paste URL]
    F --> G[Tap Generate]
    G --> H[Processing Bottom Sheet]
    H --> I[Swipe Up to View Results]
    I --> J[Horizontal Scroll Cards]
    J --> K[Tap Card to Preview]
    K --> L[Full Screen Preview]
    L --> M[Tap Copy Button]
    M --> N[Copied Toast]
    N --> O{Next?}
    O -->|Share| P[Share Sheet]
    O -->|Done| Q[Close/Back]
    O -->|Copy More| J
```

---

## Journey 8: Search & Filter in Library

```mermaid
graph TD
    A[Open Library] --> B[See All Content]
    B --> C{Action?}
    
    C -->|Search| D[Type in Search]
    D --> E[See Results]
    E --> F{Found It?}
    F -->|Yes| G[Click Content]
    F -->|No| H[Clear Search]
    H --> C
    
    C -->|Filter| I[Open Filters]
    I --> J[Select Type]
    J --> K[Select Date Range]
    K --> L[Apply Filters]
    L --> M[See Filtered Results]
    M --> N{More Filters?}
    N -->|Yes| I
    N -->|No| G
    
    C -->|Sort| O[Change Sort Order]
    O --> P[Results Reorder]
    P --> G
    
    G[Click Content] --> Q[View/Edit]
```

---

## Journey 9: Bulk Export Workflow

```mermaid
graph TD
    A[Library with Multiple Items] --> B[Select Items]
    B --> C{How Many?}
    C -->|Select All| D[Click Select All]
    C -->|Choose Specific| E[Click Checkboxes]
    
    D --> F[N Items Selected]
    E --> F
    
    F --> G[Click Export Button]
    G --> H[Export Modal Opens]
    H --> I[Choose Format]
    I --> J{Format?}
    
    J -->|JSON| K[Select JSON]
    J -->|CSV| L[Select CSV]
    J -->|Text| M[Select TXT]
    
    K --> N[Configure Options]
    L --> N
    M --> N
    
    N --> O[Include Metadata?]
    O --> P[Compress as ZIP?]
    P --> Q[Click Export]
    Q --> R[Generating File...]
    R --> S[Download Starts]
    S --> T[Success Toast]
    T --> U[Modal Closes]
```

---

## Journey 10: Style Preset Management

```mermaid
graph TD
    A[Settings] --> B[Style Presets Section]
    B --> C{Action?}
    
    C -->|Create New| D[Click Create]
    D --> E[Modal Opens]
    E --> F[Enter Name]
    F --> G[Set Target Audience]
    G --> H[Set Tone]
    H --> I[Set Language]
    I --> J[Set CTA]
    J --> K[Optional Instructions]
    K --> L[Click Save]
    L --> M{Valid?}
    M -->|No| N[Show Errors]
    N --> F
    M -->|Yes| O[Save Preset]
    O --> P[Success]
    
    C -->|Edit Existing| Q[Click Edit]
    Q --> R[Modal with Data]
    R --> S[Modify Fields]
    S --> L
    
    C -->|Delete| T[Click Delete]
    T --> U[Confirm Modal]
    U --> V{Confirm?}
    V -->|Yes| W[Delete Preset]
    V -->|No| B
    W --> X[Removed]
    
    P --> Y[Use in Processing]
    X --> B
```

---

## Screen Transition Map

```mermaid
graph LR
    A[Login] -->|success| B[Dashboard]
    B -->|+ New| C[Video Input]
    B -->|View Card| D[Content Detail]
    B -->|Library| E[Library]
    B -->|Bulk| F[Bulk Processing]
    B -->|Settings| G[Settings]
    
    C -->|Generate| H[Processing]
    H -->|Complete| I[Content Results]
    I -->|Edit| J[Content Editor]
    I -->|Library| E
    I -->|Process More| C
    
    E -->|Click Content| D
    E -->|Edit| J
    D -->|Edit| J
    
    F -->|Process| K[Bulk Processing Status]
    K -->|Complete| L[Bulk Results]
    L -->|View All| E
    
    J -->|Save| D
    J -->|Cancel| E
    
    G -->|Any Section| G
    
    %% All can navigate back to Dashboard
    C -.->|Nav| B
    E -.->|Nav| B
    F -.->|Nav| B
    G -.->|Nav| B
    D -.->|Nav| B
    I -.->|Nav| B
```

---

## State Transitions - Content Item

```mermaid
stateDiagram-v2
    [*] --> Draft: Generate
    Draft --> Processing: Edit Request
    Draft --> Published: Mark Published
    Draft --> Archived: Archive
    
    Processing --> Draft: Edit Complete
    Processing --> Error: Edit Failed
    
    Published --> Draft: Unpublish
    Published --> Archived: Archive
    
    Error --> Draft: Retry Success
    Error --> Archived: Give Up
    
    Archived --> Draft: Restore
    Archived --> [*]: Delete
```

---

## Authentication Flow States

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated
    Unauthenticated --> Authenticating: Login/Signup
    Authenticating --> Authenticated: Success
    Authenticating --> Unauthenticated: Failure
    
    Authenticated --> Refreshing: Token Expiring
    Refreshing --> Authenticated: Refresh Success
    Refreshing --> Unauthenticated: Refresh Failure
    
    Authenticated --> Unauthenticated: Logout
    Authenticated --> [*]
```

---

## Notes on Flow Design

### Design Principles Applied:
1. **Progressive Disclosure**: Complex options revealed only when needed
2. **Clear Feedback**: Every action has visible response
3. **Error Recovery**: Multiple paths to recover from errors
4. **Flexible Paths**: Users can achieve goals via different routes
5. **Non-Destructive**: Confirmations before destructive actions

### User Experience Highlights:
- Minimal steps to achieve primary goals
- Clear visual feedback at each step
- Multiple entry points to common tasks
- Easy error recovery
- Mobile-optimized flows
- Keyboard shortcuts for power users

### Flow Optimization:
- Reduced clicks for common tasks
- Smart defaults minimize decisions
- Batch operations for efficiency
- Background processing where possible
- Autosave prevents data loss
