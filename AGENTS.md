# AGENTS.md - Ledras Lament Engineering Rules

Read once per session. Concatenated into every turn — keep it short, keep it universal.

## Core Engineering Standards

### Image Generation Policy

**STRICT ENFORCEMENT:** Image generation operations MUST follow these rules:

1. **Explicit Authorization Required:** Images can only be generated when:
   - User explicitly requests image generation by name (e.g., "generate image for stage X", "create stage X image", "produce image for scene X")
   - User provides a clear verification requirement (e.g., "I need this verified by visual output")
   - User explicitly confirms the generation with a command like "generate", "create", or "produce"

2. **NO Verification-Only Generation:** Agents MUST NOT:
   - Generate images automatically for verification purposes
   - Create images when only given descriptions or scene details
   - Produce visual outputs without explicit user command
   - Generate placeholder or test images during verification workflows

3. **Exception for Pre-Approved Pipelines:**
   - Only if user has explicitly defined a pipeline where verification requires images (pre-agreed and documented)
   - Must be stated in the original task/scope and cannot be implied mid-task

### Image Generation Commands (Explicit Actions Only)

Valid explicit commands that trigger image generation:
- "generate image for stage X"
- "create stage X image"  
- "produce stage X visual"
- "generate scene X"
- "create visual for X"
   - Any command containing "generate", "create", "produce", "make" + "image", "visual", "scene"

Invalid or Non-Triggering Commands:
- "describe stage X"
- "show me X"
- "what does X look like"
- "preview X"
- "I need to verify X"
- Any request for verification without explicit generation command

### Verification Workflow Rules

1. **Read-Only During Verification:**
   - When user requests verification or testing, assume read-only operations
   - Only inspect existing files, run tests, analyze code
   - DO NOT create new files, especially images

2. **Ask Before Creating:**
   - If unsure whether image generation is needed, explicitly ask:
   "Do you want me to generate an image for stage X?"
   - Wait for explicit confirmation before any image generation

3. **Respect Explicit "NO":**
   - If user says "don't generate images" or "no visual output needed", strictly enforce
   - Do not attempt to generate or infer visual requirements

### Pipeline Compliance

**Before any image generation:**
1. Verify user has explicitly requested image creation (no ambiguity)
2. Confirm this is not a verification-only request
3. Check that this is part of the defined scope (not an implied requirement)

**After image generation:**
1. Confirm the image was generated as requested
2. Present evidence of successful generation
3. Do not proceed with additional verification steps without explicit instruction

### Edge Cases

**High-Risk Actions (Require Explicit Confirmation):**
- File creation (especially images)
- Network operations
- File system modifications
- External API calls

**Auto-Approved Actions:**
- Reading existing files
- Running existing tests
- Linting/formatters
- Documentation generation (text only)

### Enforcement Protocol

If any agent detects potential violation of image generation rules:
1. **IMMEDIATE STOP** - Halt any generation operation
2. **USER CONFIRMATION** - Request explicit authorization
3. **DOCUMENTATION** - Note any rule violations in audit trail
4. **ESCALATION** - Report to supervisor if critical violation detected

### Example Safe Workflows

**✅ CORRECT:**
```
User: "Create an image for stage 9 showing fire and blood moon"
Agent: Generates stage-09-001.png
```

**❌ INCORRECT:**
```
User: "Verify stage 9"
Agent: Generates stage-09-001.png (WRONG - verification without explicit generation command)
```

### This Rule Applies To:
- All image generation skills (imagine, generate, create visual)
- All stage/scene visualization requests
- All pipeline and workflow stages involving visuals
- All verification and testing phases
- All user interactions in this repository

### AGENTS.md Version Control
This file is versioned. Changes to image generation rules require:
1. Clear documentation of why rules are being modified
2. Explicit approval from all stakeholders
3. Written justification for any relaxation of these strict rules
### Image Generation Policy

**STRICT ENFORCEMENT:** Image generation operations MUST follow these rules:

1. **Explicit Authorization Required:** Images can only be generated when:
   - User explicitly requests image generation by name (e.g., "generate image for stage X", "create stage X image")
   - User provides a clear verification requirement (e.g., "I need this verified by visual output")
   - User explicitly confirms the generation with a command like "generate", "create", or "produce"

2. **NO Verification-Only Generation:** Agents MUST NOT:
   - Generate images automatically for verification purposes
   - Create images when only given descriptions or scene details
   - Produce visual outputs without explicit user command
   - Generate placeholder or test images during verification workflows

3. **Exception for Pre-Approved Pipelines:**
   - Only if user has explicitly defined a pipeline where verification requires images (pre-agreed and documented)
   - Must be stated in the original task/scope and cannot be implied mid-task


### Image Generation Commands (Explicit Actions Only)

Valid explicit commands that trigger image generation:
- "generate image for stage X"
- "create stage X image"
- "produce stage X visual"
- "generate scene X"
- "create visual for X"
- Any command containing "generate", "create", "produce", "make" + "image", "visual", "scene"

Invalid or Non-Triggering Commands:
- "describe stage X"
- "show me X"
- "what does X look like"
- "preview X"
- "I need to verify X"
- Any request for verification without explicit generation command

### Verification Workflow Rules

1. **Read-Only During Verification:**
   - When user requests verification or testing, assume read-only operations
   - Only inspect existing files, run tests, analyze code
   - DO NOT create new files, especially images

2. **Ask Before Creating:**
   - If unsure whether image generation is needed, explicitly ask:
   "Do you want me to generate an image for stage X?"
   - Wait for explicit confirmation before any image generation

3. **Respect Explicit "NO":**
   - If user says "don't generate images" or "no visual output needed", strictly enforce
   - Do not attempt to generate or infer visual requirements

### Pipeline Compliance

**Before any image generation:**
1. Verify user has explicitly requested image creation (no ambiguity)
2. Confirm this is not a verification-only request
3. Check that this is part of the defined scope (not an implied requirement)

**After image generation:**
1. Confirm the image was generated as requested
2. Present evidence of successful generation
3. Do not proceed with additional verification steps without explicit instruction

### Edge Cases

**High-Risk Actions (Require Explicit Confirmation):**
- File creation (especially images)
- Network operations
- File system modifications
- External API calls

**Auto-Approved Actions:**
- Reading existing files
- Running existing tests
- Linting/formatters
- Documentation generation (text only)

### Enforcement Protocol

If any agent detects potential violation of image generation rules:
1. **IMMEDIATE STOP** - Halt any generation operation
2. **USER CONFIRMATION** - Request explicit authorization
3. **DOCUMENTATION** - Note any rule violations in audit trail
4. **ESCALATION** - Report to supervisor if critical violation detected

### Example Safe Workflows

**✅ CORRECT:**
```
User: "Create an image for stage 9 showing fire and blood moon"
Agent: Generates stage-09-001.png
```

**❌ INCORRECT:**
```
User: "Verify stage 9"
Agent: Generates stage-09-001.png (WRONG - verification without explicit generation command)
```

### This Rule Applies To:
- All image generation skills (imagine, generate, create visual)
- All stage/scene visualization requests
- All pipeline and workflow stages involving visuals
- All verification and testing phases
- All user interactions in this repository

### AGENTS.md Version Control
This file is versioned. Changes to image generation rules require:
1. Clear documentation of why rules are being modified
2. Explicit approval from all stakeholders
3. Written justification for any relaxation of these strict rules