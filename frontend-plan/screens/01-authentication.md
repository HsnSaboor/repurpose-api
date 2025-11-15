# Authentication Screens

## Overview
Simple, trust-building authentication flow. Split-screen design on desktop, full-screen on mobile.

---

## Screen: Login

### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  [LEFT HALF - Brand/Visual]    [RIGHT HALF - Form]     │
│                                                         │
│  Logo                           Welcome Back            │
│                                                         │
│  Headline                       Email                   │
│  Subheadline                    [____________]          │
│                                                         │
│  [Feature bullets]              Password                │
│  • Point 1                      [____________]          │
│  • Point 2                      [Show] [Forgot?]        │
│  • Point 3                                              │
│                                 [ Remember me ]         │
│  [Illustration/Screenshot]                              │
│                                 [Sign In Button]        │
│                                                         │
│                                 ─── or ───              │
│                                                         │
│                                 [Google Sign In]        │
│                                                         │
│                                 Don't have an account?  │
│                                 Sign Up                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Desktop (≥768px)
- Split 50/50 or 40/60 (brand/form)
- Fixed left side, scrollable right
- Min-height: 100vh

### Mobile (<768px)
- Stack vertically
- Brand section: Small header (logo + tagline)
- Form: Full width with padding

### Component Details

#### Left Panel (Brand)
```
Background: Gradient (--primary subtle to transparent)
Padding: 64px
Color: --foreground

Logo: 48px height
Headline: display-md (48px)
Subheadline: body-lg, --muted-foreground
Bullets: body, checkmark icons
Illustration: Max 400px width, rounded corners
```

#### Right Panel (Form)
```
Background: --background
Padding: 64px 48px
Max-width: 480px
Margin: auto

Title: h1 (36px)
Subtitle: body, --muted-foreground

Form:
  Field spacing: 20px
  Label: label (14px, medium)
  Input: Default size (40px)
  
Remember checkbox:
  Aligned left, body-sm
  
Forgot password:
  Link, body-sm, right-aligned
  Color: --primary
  
Sign In button:
  Full width, primary, large (48px)
  
Divider:
  "or" text centered
  
Google button:
  Full width, secondary, large
  Icon + text
  
Sign up link:
  Centered, body-sm
  Regular text + link
```

### States & Interactions

**Empty State**
- Fields empty
- Sign In button enabled but inactive color

**Typing**
- Field gains focus ring
- Show button reveals password
- Clear icon appears if has value

**Validation**
- Email format validated on blur
- Password required (min 8 chars)
- Error messages inline below field
- Shake animation on submit error

**Loading**
- Sign In button: Spinner + "Signing in..."
- Disable all inputs
- Disable social buttons

**Error**
- Toast notification at top
- Red border on affected field
- Error message below field
- Auto-focus first error field

**Success**
- Brief checkmark animation
- Transition to dashboard (300ms fade)

### Responsive Behavior

**Tablet (768px - 1024px)**
- Maintain split layout
- Reduce paddings to 40px
- Smaller illustration

**Mobile (<768px)**
- Single column
- Brand section: Logo + one-liner (24px padding)
- Form: Full width (16px padding)
- Buttons: Full width
- Smaller typography (h1 → 28px)

---

## Screen: Sign Up

### Layout Structure
Similar to login but:
- More fields (Name, Email, Password, Confirm Password)
- Password strength indicator
- Terms & conditions checkbox
- "Already have account? Sign In" at bottom

### Additional Components

**Password Strength**
```
Below password field
Bar: 4px height, full width
Colors: Red → Amber → Green
Text: "Weak" / "Fair" / "Strong"
Font: caption, color matches bar
Criteria list (optional):
  • 8+ characters
  • One uppercase
  • One number
  • One special char
```

**Terms Checkbox**
```
Body-sm text
Link to terms and privacy policy
Required to submit
```

### Form Fields
1. Full Name (required)
2. Email (required, validated)
3. Password (required, min 8 chars)
4. Confirm Password (must match)
5. Terms checkbox (required)

### Validation
- All fields validated on blur
- Password match checked in real-time
- Show validation checkmarks for valid fields
- Disable submit until all valid

---

## Screen: Forgot Password

### Simplified Layout
```
┌─────────────────────────────┐
│                             │
│    [Center Card]            │
│                             │
│    [Lock Icon]              │
│    Forgot Password?         │
│                             │
│    Enter your email...      │
│                             │
│    Email                    │
│    [_______________]        │
│                             │
│    [Send Reset Link]        │
│                             │
│    Back to Sign In          │
│                             │
└─────────────────────────────┘
```

### Layout
- Centered card (max-width: 440px)
- Padding: 48px
- Icon: 48px, --muted-foreground
- Title: h2
- Description: body, --muted-foreground
- Form: Single email field
- Button: Full width, primary
- Back link: Centered, body-sm

### States

**Email Sent Success**
```
Replace form with:
- Green checkmark icon
- "Check your email" heading
- Instructions with email shown
- "Resend email" button (ghost)
- "Back to Sign In" link
```

---

## Screen: Reset Password

### Layout
Similar to Forgot Password but:
- Password field
- Confirm password field
- Password strength indicator
- Reset button

### Flow
1. User clicks link from email
2. Token validated on load
3. If invalid: Show error + request new link
4. If valid: Show form
5. On success: Redirect to login with success toast

---

## Common Elements

### Social Sign In Buttons
```
Width: Full width
Height: 48px
Border: 1px solid --border
Background: --card
Border-radius: --radius

Hover: --muted background

Icon: 20px, left side (16px margin)
Text: body, medium, centered
Gap: 12px

Providers:
- Google (multicolor icon)
- GitHub (optional)
```

### Loading Overlay
```
Full screen semi-transparent backdrop
Centered spinner + "Loading..." text
Prevents interaction
```

### Validation Icons
```
Inside input (right side)
16px size
Colors:
  Success: --success (checkmark)
  Error: --destructive (×)
Position: 12px from right edge
```

---

## Accessibility

- All form fields have labels
- Error messages associated via aria-describedby
- Password show/hide has aria-label
- Focus trap in modals
- Keyboard navigation (Tab, Enter)
- Screen reader announcements for errors
- Color not sole indicator (icons + text)

---

## User Interactions Summary

### Login Flow
1. User lands on login
2. Enters email, password
3. Optionally checks "Remember me"
4. Clicks "Sign In" or presses Enter
5. → Success: Dashboard
6. → Error: Show message, stay on page
7. Alternative: Click "Sign in with Google"
   → OAuth flow → Dashboard

### Sign Up Flow
1. User clicks "Sign Up" from login
2. Fills all fields
3. Password strength updates in real-time
4. Confirm password validates match
5. Checks terms checkbox
6. Clicks "Sign Up"
7. → Success: Welcome email sent, redirect to onboarding or dashboard
8. → Error: Show validation errors

### Forgot Password Flow
1. User clicks "Forgot password?"
2. Enters email
3. Clicks "Send Reset Link"
4. → Success: Shows confirmation screen
5. Checks email, clicks link
6. Enters new password
7. Submits reset form
8. → Success: Redirect to login with toast

---

## Design Notes

- Keep forms simple and uncluttered
- Use plenty of whitespace
- Make CTAs prominent and clear
- Provide helpful error messages
- Don't ask for unnecessary information
- Make password requirements clear upfront
- Allow social sign-in for convenience
- Remember me is optional, not pre-checked
- Link to help/support visible
