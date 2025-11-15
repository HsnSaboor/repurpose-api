# Settings Screen

## Overview
Configuration hub for account, content generation, API keys, and style presets. Organized into clear sections with tab navigation.

---

## Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│ [Top Nav]                                                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Settings                                          │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌──────────┬───────────────────────────────────────────┐   │
│  │          │                                           │   │
│  │ Sidebar  │  Content Area                             │   │
│  │          │                                           │   │
│  │ • Account│  ┌─────────────────────────────────────┐ │   │
│  │ • Content│  │  Section Content                    │ │   │
│  │   Config │  │                                     │ │   │
│  │ • API    │  │  [Settings Form]                    │ │   │
│  │   Keys   │  │                                     │ │   │
│  │ • Style  │  │                                     │ │   │
│  │   Presets│  │                                     │ │   │
│  │ • Billing│  │                                     │ │   │
│  │          │  └─────────────────────────────────────┘ │   │
│  │          │                                           │   │
│  └──────────┴───────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Layout: Sidebar + Content

### Sidebar (Desktop)

```
Width: 240px
Background: --card
Border-right: 1px solid --border
Padding: 24px 16px
Position: sticky
Height: calc(100vh - 64px)

Navigation items:
  ┌─────────────────────┐
  │ ► Account           │ ← Active
  │   Content Config    │
  │   API Keys          │
  │   Style Presets     │
  │   Billing           │
  │   Preferences       │
  │   About             │
  └─────────────────────┘
  
Item style:
  Padding: 12px 16px
  Border-radius: --radius
  Font: body-sm, medium
  Color: --foreground
  Gap: 12px (icon + text)
  
  Hover: --muted background
  Active: --primary/10 bg, --primary text, left border
  
  Icon: 20px
  
Mobile: Hide, show hamburger or tabs
```

### Content Area

```
Flex: 1
Padding: 32px
Max-width: 800px
Overflow: auto

Structure:
  Section title (h2, 30px)
  Description (body, --muted-foreground)
  
  Form sections with clear separations
  
  Save changes footer (sticky bottom)
```

---

## Section: Account

```
┌─────────────────────────────────────────────────┐
│ Account Settings                                │
│ Manage your account information and preferences │
├─────────────────────────────────────────────────┤
│                                                 │
│ Profile Information                             │
│ ─────────────                                   │
│                                                 │
│ [Avatar - 80px circle]  [Upload] [Remove]      │
│                                                 │
│ Full Name                                       │
│ [________________________________]              │
│                                                 │
│ Email                                           │
│ [________________________________]              │
│ This is your login email                        │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Password                                        │
│ ─────────                                       │
│                                                 │
│ ••••••••  [Change Password]                     │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Danger Zone                                     │
│ ──────────                                      │
│                                                 │
│ [Delete Account]                                │
│ This action cannot be undone                    │
│                                                 │
├─────────────────────────────────────────────────┤
│                        [Cancel] [Save Changes]  │
└─────────────────────────────────────────────────┘

Components:
- Avatar upload with preview
- Standard text inputs
- Change password opens modal
- Delete account confirmation flow
- Save changes button (sticky)
```

---

## Section: Content Configuration

```
┌─────────────────────────────────────────────────┐
│ Content Generation Configuration                │
│ Customize content generation settings           │
├─────────────────────────────────────────────────┤
│                                                 │
│ Content Ideas Range                             │
│ ───────────────────                             │
│                                                 │
│ Minimum Ideas       Maximum Ideas               │
│ [6 ▼]              [8 ▼]                        │
│ How many content ideas to generate per video    │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Field Length Limits                             │
│ ───────────────────                             │
│                                                 │
│ Reel Settings                                   │
│   Title max length:     [100] characters        │
│   Caption max length:   [300] characters        │
│   Hook max length:      [200] characters        │
│   Script max length:    [2000] characters       │
│                                                 │
│ Carousel Settings                               │
│   Title max length:     [100] characters        │
│   Caption max length:   [300] characters        │
│   Slide heading max:    [100] characters        │
│   Slide text max:       [800] characters        │
│   Min slides:           [4 ▼]                   │
│   Max slides:           [8 ▼]                   │
│                                                 │
│ Tweet Settings                                  │
│   Title max length:     [100] characters        │
│   Tweet max length:     [280] characters        │
│   Thread item max:      [280] characters        │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ [Reset to Defaults]                             │
│                                                 │
├─────────────────────────────────────────────────┤
│                        [Cancel] [Save Changes]  │
└─────────────────────────────────────────────────┘

Components:
- Number inputs with validation
- Dropdowns for ranges
- Sliders (optional for character limits)
- Helper text for each setting
- Preview of current config
- Reset button
```

---

## Section: API Keys

```
┌─────────────────────────────────────────────────┐
│ API Keys & Integrations                         │
│ Manage API keys for external services           │
├─────────────────────────────────────────────────┤
│                                                 │
│ Gemini API Key                                  │
│ ──────────────                                  │
│                                                 │
│ [••••••••••••••••••••••••••abcd] [Show] [Edit] │
│ Used for AI content generation                  │
│                                                 │
│ Status: ✓ Valid  Last checked: 2 min ago       │
│                                                 │
│ [Test Connection]                               │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ YouTube API (Optional)                          │
│ ──────────────────────                          │
│                                                 │
│ Not configured  [Add API Key]                   │
│ Required only for private videos                │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Webhook URL (Advanced)                          │
│ ──────────────────────                          │
│                                                 │
│ [________________________________]              │
│ Receive notifications when processing completes │
│                                                 │
├─────────────────────────────────────────────────┤
│                        [Cancel] [Save Changes]  │
└─────────────────────────────────────────────────┘

Components:
- Masked input with show/hide
- Test connection button
- Status indicators
- Optional fields clearly marked
- Secure handling warnings
```

---

## Section: Style Presets

```
┌─────────────────────────────────────────────────┐
│ Style Presets                                   │
│ Manage content style presets                    │
├─────────────────────────────────────────────────┤
│                                                 │
│ [+ Create New Preset]                           │
│                                                 │
│ ┌───────────────────────────────────────────┐  │
│ │ Professional Business          [Edit] [×] │  │
│ │ Target: Business professionals            │  │
│ │ Tone: Professional & authoritative        │  │
│ │ Language: English                         │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ ┌───────────────────────────────────────────┐  │
│ │ Social Media Casual            [Edit] [×] │  │
│ │ Target: Young social media users          │  │
│ │ Tone: Casual & friendly                   │  │
│ │ Language: English                         │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ ┌───────────────────────────────────────────┐  │
│ │ E-commerce Entrepreneur        [Edit] [×] │  │
│ │ Target: Shopify store owners              │  │
│ │ Tone: Motivational                        │  │
│ │ Language: Roman Urdu                      │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘

Preset card:
  Background: --card
  Border: 1px solid --border
  Border-radius: --radius-lg
  Padding: 20px
  Margin-bottom: 16px
  
  Hover: Shadow, border stronger
  
  Header: Title + actions
  Body: Key info preview
  
Actions:
  [Edit] → Open edit modal
  [×] → Delete (with confirmation)
  [Duplicate] (in menu)
```

### Create/Edit Preset Modal

```
┌─────────────────────────────────────────────┐
│ Create Style Preset             [×]         │
├─────────────────────────────────────────────┤
│                                             │
│ Preset Name *                               │
│ [_____________________________]             │
│                                             │
│ Description                                 │
│ [_____________________________]             │
│                                             │
│ Target Audience *                           │
│ [_____________________________]             │
│                                             │
│ Content Goal *                              │
│ [_____________________________]             │
│ E.g., "education, lead generation"          │
│                                             │
│ Tone *                                      │
│ [_____________________________]             │
│ E.g., "Professional, inspiring"             │
│                                             │
│ Language *                                  │
│ [English ▼]                                 │
│                                             │
│ Call to Action                              │
│ [_____________________________]             │
│                                             │
│ Additional Instructions (optional)          │
│ [_____________________________              │
│  _____________________________]             │
│                                             │
├─────────────────────────────────────────────┤
│                    [Cancel] [Save Preset]   │
└─────────────────────────────────────────────┘

Validation:
- Required fields marked with *
- Real-time validation
- Example text hints
```

---

## Section: Billing (Optional)

```
┌─────────────────────────────────────────────────┐
│ Billing & Usage                                 │
│ Manage your subscription and usage              │
├─────────────────────────────────────────────────┤
│                                                 │
│ Current Plan                                    │
│ ────────────                                    │
│                                                 │
│ ┌───────────────────────────────────────────┐  │
│ │ Pro Plan              $29/month           │  │
│ │                                           │  │
│ │ • Unlimited videos                        │  │
│ │ • Priority processing                     │  │
│ │ • Advanced features                       │  │
│ │                                           │  │
│ │ [Manage Subscription]                     │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ Usage This Month                                │
│ ────────────────                                │
│                                                 │
│ Videos Processed:    45 / ∞                     │
│ [████████░░░░] 45%                              │
│                                                 │
│ API Calls:          1,234 / 10,000              │
│ [████████████] 12%                              │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Payment Method                                  │
│ ──────────────                                  │
│                                                 │
│ •••• 4242  Expires 12/25  [Update]              │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Billing History                                 │
│ ───────────────                                 │
│                                                 │
│ Jan 2024   $29.00   Paid   [Invoice ↓]         │
│ Dec 2023   $29.00   Paid   [Invoice ↓]         │
│ Nov 2023   $29.00   Paid   [Invoice ↓]         │
│                                                 │
│ [View All Invoices]                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Section: Preferences

```
┌─────────────────────────────────────────────────┐
│ Preferences                                     │
│ Customize your experience                       │
├─────────────────────────────────────────────────┤
│                                                 │
│ Appearance                                      │
│ ──────────                                      │
│                                                 │
│ Theme                                           │
│ ⚪ Light  ⚪ Dark  ⚪ System                     │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Notifications                                   │
│ ─────────────                                   │
│                                                 │
│ ☑ Email notifications                           │
│ ☑ Processing complete alerts                    │
│ ☐ Weekly summary reports                        │
│ ☐ Product updates                               │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Default Settings                                │
│ ────────────────                                │
│                                                 │
│ Default style preset:                           │
│ [Professional Business ▼]                       │
│                                                 │
│ Auto-copy on generation:                        │
│ ☐ Enabled                                       │
│                                                 │
│ Content view preference:                        │
│ ⚪ Grid  ⚪ List                                 │
│                                                 │
├─────────────────────────────────────────────────┤
│                        [Cancel] [Save Changes]  │
└─────────────────────────────────────────────────┘
```

---

## Section: About

```
┌─────────────────────────────────────────────────┐
│ About                                           │
│ Version information and support                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ YouTube Repurposer                              │
│ Version 2.1.0                                   │
│                                                 │
│ Transform YouTube videos into engaging social   │
│ media content with AI.                          │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Resources                                       │
│ • Documentation                                 │
│ • API Reference                                 │
│ • Community Forum                               │
│ • GitHub Repository                             │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Support                                         │
│ • Contact Support                               │
│ • Report a Bug                                  │
│ • Request a Feature                             │
│                                                 │
│ ──────────────────────────────────              │
│                                                 │
│ Legal                                           │
│ • Terms of Service                              │
│ • Privacy Policy                                │
│ • License                                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Responsive Behavior

### Desktop (≥1024px)
- Sidebar + content layout
- Full width forms (max 800px)
- All sections accessible

### Tablet (768px - 1023px)
- Collapsible sidebar OR tabs
- Slightly narrower content
- Maintain functionality

### Mobile (<768px)
- Tabs instead of sidebar
- Full width forms
- Stack elements vertically
- Bottom save bar (sticky)

---

## User Interactions

### Navigation
1. Click sidebar item → Load section
2. URL updates: /settings/account
3. Scroll to top of content
4. Active state on sidebar

### Form Changes
1. User modifies any field
2. "Save Changes" button enables
3. Unsaved changes warning on navigate
4. Form validation on blur

### Save Changes
1. Click "Save Changes"
2. Validate all fields
3. API call to update
4. Success toast or error message
5. Disable button again

### Test Connection (API Keys)
1. Click "Test Connection"
2. API call to validate key
3. Show loading state
4. Display result: ✓ Valid or ✗ Invalid

### Style Preset Management
1. **Create**: Modal opens → Fill form → Save
2. **Edit**: Modal with pre-filled data → Update → Save
3. **Delete**: Confirm modal → Delete → Remove from list
4. **Duplicate**: Copy preset → Open edit modal with copy

---

## Data Requirements

```javascript
// Get user settings
GET /settings/
Response: {
  account: {...}
  content_config: {...}
  api_keys: {...}
  style_presets: [...]
  preferences: {...}
}

// Update account
PUT /settings/account
Body: {...}

// Update content config
PUT /settings/content-config
Body: {...}

// Update API keys
PUT /settings/api-keys
Body: {...}

// Style preset CRUD
GET /style-presets/
POST /style-presets/
PUT /style-presets/{id}
DELETE /style-presets/{id}

// Test API connection
POST /settings/test-api-key
Body: { service: "gemini", key: "..." }
Response: { valid: boolean, error?: string }
```

---

## Edge Cases

### Unsaved Changes
- Warn before navigating away
- Offer: Save, Don't Save, Cancel

### Invalid API Key
- Show error clearly
- Offer: Re-enter, Test Again, Contact Support

### Failed Save
- Show error message
- Keep form data
- Offer retry

### Validation Errors
- Highlight all errors
- Scroll to first error
- Block save until fixed

---

## Accessibility

- Keyboard navigation through sections
- Focus management
- ARIA labels for all inputs
- Error messages associated with fields
- Screen reader announcements for saves
- High contrast support
- Logical tab order
