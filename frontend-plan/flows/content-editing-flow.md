# Content Editing Flow

## Detailed Content Editing Architecture & User Flow

---

## High-Level Editing Flow

```mermaid
graph TB
    subgraph "Entry Points"
        A1[From Library] --> B[Select Content]
        A2[From Generation Results] --> B
        A3[From Dashboard] --> B
    end
    
    subgraph "Editor Interface"
        B --> C[Load Content]
        C --> D[Display Editor]
        D --> E{Editing Mode}
        
        E -->|AI Edit| F[Natural Language Prompt]
        E -->|Manual Edit| G[Direct Field Editing]
        
        F --> H[Submit to AI]
        G --> I[Update Preview]
        
        H --> J[AI Processing]
        J --> K[Apply Changes]
        K --> I
        
        I --> L{Satisfied?}
        L -->|No| E
        L -->|Yes| M[Save Changes]
    end
    
    subgraph "Persistence"
        M --> N[Validate Changes]
        N --> O{Valid?}
        O -->|No| P[Show Errors]
        P --> E
        O -->|Yes| Q[Update Database]
        Q --> R[Success]
    end
    
    subgraph "Exit"
        R --> S{Next Action}
        S -->|Copy| T[Copy to Clipboard]
        S -->|Edit Another| B
        S -->|Done| U[Return to Library]
    end
```

---

## AI Edit Flow Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI
    participant Frontend
    participant Backend
    participant AI Service
    participant DB
    
    User->>UI: Opens Editor
    UI->>Frontend: Load content ID
    Frontend->>Backend: GET /content/{id}
    Backend->>DB: Fetch content
    DB->>Backend: Content data
    Backend->>Frontend: Content + original
    Frontend->>UI: Display editor
    UI->>User: Show content + controls
    
    User->>UI: Types edit prompt
    Note over User,UI: "Make it more engaging<br/>and add emojis"
    
    User->>UI: Click "Apply Edit"
    UI->>Frontend: Submit prompt
    Frontend->>Backend: POST /edit-content
    activate Backend
    
    Backend->>AI Service: Send prompt + content
    activate AI Service
    Note over AI Service: LLM processes request<br/>Applies changes<br/>Maintains structure
    AI Service->>Backend: Edited content
    deactivate AI Service
    
    Backend->>Backend: Validate edited content
    
    alt Validation Failed
        Backend->>AI Service: Retry with constraints
        AI Service->>Backend: Fixed content
    end
    
    Backend->>Backend: Track changes
    Backend->>Frontend: Return edited content
    deactivate Backend
    
    Frontend->>UI: Update preview
    UI->>User: Show changes
    
    alt User Saves
        User->>UI: Click "Save"
        UI->>Frontend: Confirm save
        Frontend->>Backend: PUT /content/{id}
        Backend->>DB: Update content
        DB->>Backend: Confirm
        Backend->>Frontend: Success
        Frontend->>UI: Show success toast
    else User Reverts
        User->>UI: Click "Revert"
        UI->>Frontend: Discard changes
        Frontend->>UI: Restore original
    end
```

---

## Manual Edit Flow

```mermaid
graph TD
    A[Switch to Manual Tab] --> B[Show Form Fields]
    B --> C[User Edits Field]
    C --> D[Debounced Update]
    D --> E[Update Preview]
    E --> F[Validate Field]
    
    F --> G{Valid?}
    G -->|No| H[Show Inline Error]
    H --> I[Disable Save]
    G -->|Yes| J[Mark as Changed]
    J --> K[Enable Save]
    
    C --> C
    
    K --> L{User Continues?}
    L -->|Edit More| C
    L -->|Save| M[Click Save Button]
    
    M --> N[Validate All Fields]
    N --> O{All Valid?}
    O -->|No| P[Highlight Errors]
    P --> Q[Focus First Error]
    Q --> C
    O -->|Yes| R[Submit Changes]
    R --> S[Update Database]
    S --> T[Success Toast]
    T --> U[Stay or Navigate]
```

---

## State Management

```mermaid
stateDiagram-v2
    [*] --> Loading: Open Editor
    Loading --> Loaded: Content Fetched
    Loading --> Error: Fetch Failed
    
    Error --> Loading: Retry
    Error --> [*]: Cancel
    
    Loaded --> Editing: User Changes Content
    Editing --> Validating: Submit Changes
    Editing --> Loaded: Revert
    
    Validating --> ValidationError: Invalid
    Validating --> Saving: Valid
    
    ValidationError --> Editing: Fix Errors
    
    Saving --> Saved: Success
    Saving --> SaveError: Failure
    
    SaveError --> Editing: Retry
    
    Saved --> [*]: Exit
    Saved --> Loaded: Edit More
    
    note right of Editing: Changes tracked<br/>Preview updates<br/>Save enabled
    
    note right of Saved: Success feedback<br/>DB updated<br/>Can continue or exit
```

---

## Real-time Preview Updates

```mermaid
graph LR
    A[User Types] --> B[Debounce 300ms]
    B --> C[Update State]
    C --> D[Re-render Preview]
    D --> E[Validate Field]
    E --> F{Valid?}
    F -->|Yes| G[Show Checkmark]
    F -->|No| H[Show Error]
    
    G --> I[Update Character Count]
    H --> I
    I --> J[Enable/Disable Save]
    
    K[Parallel: Save Draft] -.-> L[LocalStorage]
    C -.-> K
    
    M[On Unmount] -.-> N[Clear Draft]
```

---

## Quick Edit Presets Flow

```mermaid
graph TD
    A[User in Editor] --> B[See Quick Edit Chips]
    B --> C{Action}
    
    C -->|Single Click| D[Populate Prompt Field]
    D --> E[User Can Modify]
    E --> F[Click Apply Edit]
    
    C -->|Double Click| G[Apply Immediately]
    G --> H[Show Loading]
    
    F --> H
    
    H --> I[AI Processing]
    I --> J[Preview Updates]
    J --> K{Satisfied?}
    
    K -->|No| L[Try Different Preset]
    L --> C
    K -->|Yes| M[Save Changes]
    
    Presets:
    P1[Make Professional]
    P2[Add Emojis]
    P3[Shorten Text]
    P4[Expand Details]
    P5[More Engaging]
    P6[Add CTA]
```

---

## Edit History Management

```mermaid
sequenceDiagram
    participant UI
    participant State
    participant History
    participant Backend
    
    UI->>State: Apply Edit #1
    State->>History: Push to history stack
    Note over History: ["Original", "Edit 1"]
    
    UI->>State: Apply Edit #2
    State->>History: Push to stack
    Note over History: ["Original", "Edit 1", "Edit 2"]
    
    UI->>UI: User clicks "Undo"
    UI->>History: Pop from stack
    History->>State: Restore "Edit 1"
    State->>UI: Update preview
    
    UI->>UI: User clicks "Undo" again
    UI->>History: Pop from stack
    History->>State: Restore "Original"
    State->>UI: Update preview
    
    UI->>State: Apply new Edit #3
    State->>History: Push to stack
    Note over History: ["Original", "Edit 3"]<br/>Edit 1 & 2 discarded
    
    UI->>UI: User saves
    UI->>Backend: PUT /content
    Backend->>State: Confirm saved
    State->>History: Clear future edits
    Note over History: History locked at save
```

---

## Comparison Mode Flow

```mermaid
graph TB
    A[Toggle Compare Mode] --> B[Split Preview]
    B --> C[Left: Original]
    B --> D[Right: Current]
    
    C --> E[Highlight Deletions]
    D --> F[Highlight Additions]
    D --> G[Highlight Changes]
    
    E --> H[Visual Diff]
    F --> H
    G --> H
    
    H --> I{User Review}
    I -->|Accept| J[Keep Changes]
    I -->|Revert| K[Restore Original]
    I -->|Toggle Off| L[Return to Single View]
    
    J --> M[Continue Editing]
    K --> M
    L --> M
```

---

## Validation Flow Details

```mermaid
graph TD
    A[Content Changed] --> B[Run Validators]
    
    B --> C[Check Required Fields]
    C --> D{All Present?}
    D -->|No| E[Error: Missing Fields]
    D -->|Yes| F[Check Length Limits]
    
    F --> G{Within Limits?}
    G -->|No| H[Error: Too Long/Short]
    G -->|Yes| I[Check Format]
    
    I --> J{Valid Format?}
    J -->|No| K[Error: Invalid Format]
    J -->|Yes| L[All Valid]
    
    E --> M[Show Error Messages]
    H --> M
    K --> M
    M --> N[Disable Save]
    M --> O[Highlight Fields]
    
    L --> P[Enable Save]
    L --> Q[Show Success Icons]
```

---

## Carousel Slide Editing Flow

```mermaid
graph TB
    A[Edit Carousel] --> B[Display Slide List]
    B --> C[Accordion/Tabs View]
    
    C --> D{User Action}
    
    D -->|Edit Slide| E[Expand Slide]
    E --> F[Edit Heading]
    F --> G[Edit Text]
    G --> H[Preview Updates]
    
    D -->|Reorder| I[Drag Slide]
    I --> J[Update Order]
    J --> K[Renumber Slides]
    
    D -->|Add Slide| L[Click Add Button]
    L --> M[Insert New Slide]
    M --> N[Populate Template]
    N --> E
    
    D -->|Delete Slide| O[Click Delete]
    O --> P[Confirm Modal]
    P --> Q{Confirm?}
    Q -->|Yes| R[Remove Slide]
    Q -->|No| C
    R --> S[Update Indices]
    
    H --> T[Validate Slide]
    S --> T
    T --> U{Valid?}
    U -->|Yes| V[Mark Complete]
    U -->|No| W[Show Errors]
    W --> E
    
    V --> X{More Edits?}
    X -->|Yes| C
    X -->|No| Y[Save All Slides]
```

---

## Auto-save & Draft Management

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant DraftManager
    participant LocalStorage
    participant Backend
    
    User->>UI: Start editing
    UI->>DraftManager: Initialize draft
    DraftManager->>LocalStorage: Check for saved draft
    
    alt Draft Exists
        LocalStorage->>DraftManager: Return draft
        DraftManager->>UI: Restore modal
        Note over UI: "You have unsaved changes.<br/>Restore or discard?"
        User->>UI: Choose restore
        UI->>DraftManager: Load draft
    else No Draft
        Note over DraftManager: Start fresh
    end
    
    loop Every 5 seconds
        UI->>DraftManager: Check if changed
        alt Has Changes
            DraftManager->>LocalStorage: Save draft
            Note over LocalStorage: Saved locally
        end
    end
    
    alt User Saves Successfully
        UI->>Backend: PUT /content
        Backend->>UI: Success
        UI->>DraftManager: Clear draft
        DraftManager->>LocalStorage: Remove draft
    else User Closes Without Saving
        UI->>User: "Unsaved changes?"
        alt User Abandons
            User->>UI: Confirm discard
            UI->>DraftManager: Clear draft
        else User Cancels
            Note over User,UI: Stay in editor
        end
    end
```

---

## Error Recovery in Editing

```mermaid
graph TD
    A[Error Occurs] --> B{Error Type}
    
    B -->|Network Error| C[Show Offline Banner]
    C --> D[Queue Changes Locally]
    D --> E[Wait for Connection]
    E --> F{Online Again?}
    F -->|Yes| G[Sync Changes]
    F -->|No| E
    
    B -->|Validation Error| H[Highlight Issues]
    H --> I[Show Suggestions]
    I --> J[User Fixes]
    J --> K[Re-validate]
    
    B -->|AI Service Error| L[Show AI Error]
    L --> M{Retry?}
    M -->|Yes| N[Retry with Backoff]
    M -->|No| O[Switch to Manual]
    
    B -->|Save Error| P[Show Error Toast]
    P --> Q[Keep Changes in Memory]
    Q --> R[Offer Retry]
    R --> S{Retry?}
    S -->|Yes| T[Attempt Save Again]
    S -->|No| U[Export as Backup]
    
    G --> V[Success]
    K --> V
    N --> W{Success?}
    W -->|Yes| V
    W -->|No| L
    O --> V
    T --> X{Success?}
    X -->|Yes| V
    X -->|No| P
    U --> V
```

---

## Performance Optimizations

```mermaid
graph LR
    A[Editor Mount] --> B[Lazy Load Content]
    B --> C[Initial Render]
    
    D[User Types] --> E[Debounce 300ms]
    E --> F[Batch Updates]
    F --> G[Virtual DOM Diff]
    G --> H[Minimal Re-render]
    
    I[Preview Update] --> J[Memoized Component]
    J --> K[Skip if No Change]
    
    L[Large Content] --> M[Virtualize List]
    M --> N[Render Visible Only]
    
    O[AI Request] --> P[Show Loading State]
    P --> Q[Cancel Previous Request]
    Q --> R[New Request Only]
    
    S[Save Action] --> T[Optimistic Update]
    T --> U[UI Updates Immediately]
    U --> V[Backend Sync]
    V --> W{Success?}
    W -->|Yes| X[Confirm]
    W -->|No| Y[Rollback]
```

---

## Keyboard Shortcuts

```mermaid
graph TD
    A[Editor Active] --> B{Key Press}
    
    B -->|Cmd/Ctrl + S| C[Save Changes]
    B -->|Cmd/Ctrl + Z| D[Undo]
    B -->|Cmd/Ctrl + Shift + Z| E[Redo]
    B -->|Escape| F[Cancel/Close]
    B -->|Tab| G[Navigate Fields]
    B -->|Cmd/Ctrl + K| H[Quick Actions]
    B -->|Cmd/Ctrl + Enter| I[Submit AI Prompt]
    
    C --> J[Validate & Save]
    D --> K[Restore Previous]
    E --> L[Restore Next]
    F --> M[Confirm Exit]
    G --> N[Focus Next Field]
    H --> O[Open Command Palette]
    I --> P[Apply AI Edit]
```

---

## API Endpoints for Editing

```
GET /content/{content_id}
  Response: {
    content_piece: ContentPiece
    original_content: ContentPiece
    video_info: VideoInfo
  }

POST /edit-content/
  Body: {
    video_id: string
    content_piece_id: string
    edit_prompt: string
    content_type: "reel" | "carousel" | "tweet"
  }
  Response: {
    edited_content: ContentPiece
    changes_made: string[]
    status: "success"
  }

PUT /content/{content_id}
  Body: {
    content_piece: ContentPiece (modified)
  }
  Response: {
    success: boolean
    content_piece: ContentPiece (saved)
  }

GET /content/{content_id}/history
  Response: {
    edits: EditHistory[]
  }

POST /content/{content_id}/revert
  Body: {
    to_version: number
  }
  Response: {
    reverted_content: ContentPiece
  }
```

---

## Best Practices for Editing UX

### Do's:
✓ Save drafts automatically
✓ Provide real-time preview
✓ Show character counts
✓ Validate incrementally
✓ Allow undo/redo
✓ Keep edit history
✓ Offer quick presets
✓ Support keyboard shortcuts

### Don'ts:
✗ Block UI during validation
✗ Lose unsaved changes
✗ Make save button hard to find
✗ Validate on every keystroke
✗ Hide errors cryptically
✗ Require confirmation for every action
✗ Disable features without explanation

---

## Testing Scenarios

1. **Edit → Save → Success**: Standard happy path
2. **Edit → Network Fail → Retry**: Error recovery
3. **Edit → Navigate Away → Warn**: Prevent data loss
4. **Multiple Edits → Undo/Redo**: History management
5. **AI Edit → Validation Fail → Auto-retry**: Smart recovery
6. **Long Content → Performance**: Optimization check
7. **Concurrent Edit → Conflict**: Handle race conditions
8. **Auto-save → Power Loss → Restore**: Draft recovery
