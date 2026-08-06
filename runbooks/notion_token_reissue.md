# Notion Internal Integration Token Reissue Runbook

**When to use this:** Notion internal-integration token fails health check at run start, or a planned credential rotation has been initiated.

Written 2026-08-06, governed by ARCHITECTURE_PLAN.md §17.2, §6.2 (W2-11, R5-F3), and C1 §2.

---

## Blast Radius

This token gates **every fact class in both languages on every run**. A failed or missing Notion token causes the run to degrade to **research-only — knowledge base unavailable**, with zero media spend, zero text spend on generation, and only the free research sources active. This is the most critical credential in the system.

---

## Trigger Conditions

The token reissue workflow is triggered by any of the following:

1. **Run-start health check failure:** A cheap read-only health call to Notion fails with a 401 Unauthorized or "invalid credentials" error before any collection or spending. This is logged as **"the knowledge-base integration token was rejected"** per §6.2. The run automatically degrades to research-only.

2. **Planned rotation:** The operator has decided to rotate credentials as part of routine security practice (e.g., after a team member departure, quarterly refresh, or after a suspected compromise).

3. **Permission scope change:** The workspace admin has changed the integration's permissions or capabilities, and you need to reissue to reflect the new scoped access.

---

## Important: Token Non-Expiry and Revocation

**The Notion documentation states this token is non-expiring.** However, "non-expiring" does **not** mean "cannot be revoked." A workspace admin may:

- Delete the integration
- Change the integration's permissions
- Revoke scopes or database access
- Disable the integration

Any of these actions causes the token to become **invalid at use time** — it is syntactically perfect but rejected by Notion's servers. This is why a health check runs at run start (§6.2): to catch revocation before any work is attempted.

---

## Step-by-Step Reissue Process

### Step 1: Access Your Notion Workspace

1. Log in to your Notion workspace with an account that has **workspace admin** privileges. (Only workspace admins can create, modify, or delete integrations per Notion's security model.)

2. Navigate to **Settings & members → Integrations → Develop your own integrations** (exact UI path: [TO CONFIRM AT FIRST ISSUANCE]).

3. Locate the existing integration named [TO CONFIRM AT FIRST ISSUANCE — likely something like "HypeAgentSocials" or "Brand Truth Extractor"]. Click on it to view its current settings.

### Step 2: Review Current Permissions and Scope

Before reissuing, confirm that the integration has the correct scoped access:

1. In the integration details panel, check the **Capabilities** section. You should see:
   - ✓ **Read content** (required)
   - ✗ **Update content** (should NOT be checked — this is read-only)
   - ✗ **Insert content** (should NOT be checked — this is read-only)
   - ✗ **Delete content** (should NOT be checked — this is read-only)

2. Check the **Associated pages and databases** section. The integration should be scoped to **only the designated fact-location pages and databases** per §6.2 (e.g., pages named "Offers," "ICP Map," "Claims Ledger," "Hard Excludes," etc.). Do **not** grant workspace-wide access.

3. If permissions are incorrect (e.g., update/insert/delete are checked, or scope is too broad), correct them now before reissuing:
   - Uncheck any write capabilities
   - Adjust the **Associated databases and pages** list to include only the fact-location pages
   - Click **Save** if you made changes

**Why:** §6.2 mandates read-only, minimally-scoped access. A token with write permissions or workspace-wide scope is a security risk and violates the design constraint.

### Step 3: Regenerate the Token

1. In the same integration details panel, locate the **Secrets** or **API Tokens** section.

2. You should see the current token (displayed as masked characters or redacted, e.g., `secret_***...***`). Click the **"Regenerate secret"** or **"Rotate token"** button (exact label: [TO CONFIRM AT FIRST ISSUANCE]).

3. A dialog will appear asking you to confirm. Read the warning: **"A new token will be created. The old token will immediately stop working."** This is intentional. Click **Confirm** or **Regenerate**.

4. The new token will be displayed in plaintext, typically in a highlighted box. **Copy this value immediately — it is shown only once. If you close this dialog without copying, you must regenerate again.**

The new token will begin with `secret_` and is typically 40–50 characters long. Example format: `secret_abcdef1234567890ghijklmnop...`

### Step 4: Store the New Token in the Local Secret Store

**Never commit the token to the repository or any version-controlled file.**

1. Open your local secrets file or environment variable store (the location and mechanism were established during initial setup per §6.2):
   - **If environment variable:** Export as `NOTION_INTERNAL_TOKEN="<new_token_value>"`
   - **If local secrets file:** Update the entry with key `notion.internal_token` with the new token value.
   - **If Windows credential vault or similar:** [TO CONFIRM AT FIRST ISSUANCE] [exact instructions].

2. Save and verify the secret store is readable by the application. A quick test: run `echo $NOTION_INTERNAL_TOKEN` (Unix) or `$env:NOTION_INTERNAL_TOKEN` (PowerShell) and confirm the token is present (output may be truncated or masked for security).

### Step 5: Verify the Token Works with a Health Check

The health check is a single, cheap, read-only Notion API call per §6.2:

1. Run your application's initialization or startup sequence. This will trigger the **run-start health check** automatically:

   ```
   Health check: Notion API integration...
   GET https://api.notion.com/v1/users/me
   Headers: Authorization: Bearer secret_[your_token]
   ```

2. Monitor the output for the result. You should see:
   - ✓ **Status: 200 OK**
   - ✓ **User verified:** [workspace name or email]
   - ✓ **Timestamp:** [current time]

3. **If the health check fails** with 401, 403, or "unauthorized":
   - **First retry:** Stop the app, wait 5 seconds, and retry. Notion's servers may take a moment to propagate the new token.
   - **If still failing after 30 seconds:** Return to Step 4 and verify the token value character-for-character against the value shown in Step 3. **Typos in the token value are the most common cause of failure.**
   - **If still failing after verification:** The token generation may have failed on Notion's side (rare). Return to Step 3, click **"Regenerate secret"** again, and repeat Step 4.

### Step 6: Verify Scope and Read-Only Access

Once the health check passes, run a full **brand-truth resolution** test (interactive mode is fine):

1. Run a test pack with brand-truth resolution enabled. This will attempt to pull fact data from Notion using the brand-truth read path (per §6.2, a full read of the designated fact-location pages and databases).

2. Monitor the brand-truth resolution panel in the output. You should see:
   - ✓ **Notion API status: connected**
   - ✓ **Fact classes resolved:** [count of fact classes]
   - ✓ **Offers:** [name and status]
   - ✓ **Confidence band:** [FULL, PARTIAL, MINIMAL, or INSUFFICIENT depending on your data]
   - ✓ **Read-only confirmed:** (the system will not attempt any write operations; if it does, an error will appear here)

3. **If fact resolution fails** (e.g., 403 Forbidden on a specific page or database):
   - The token is authenticating, but the integration does not have permission to read that resource.
   - Return to Step 2 and verify that the failing page/database is listed in the **Associated pages and databases** section.
   - If it is not, click **Add page** or **Manage databases** and add it.
   - Save the changes and retry the brand-truth test.

4. **If any write operation is attempted** (which should never happen):
   - This indicates a misconfiguration or a bug in the application.
   - Stop immediately. Return to Step 2 and confirm that update/insert/delete capabilities are **unchecked**.
   - If they were checked, uncheck them, save, and regenerate the token (start over at Step 3).

### Step 7: Update Secrets Metadata

1. In your **secrets-metadata** file or comment block alongside your secrets (never the token itself, only the metadata), record:

   ```
   # Notion Internal Integration Token
   # Reissued: 2026-08-06
   # Scope: READ-ONLY, fact-location pages and databases only
   # Health check: PASSED
   # Capabilities verified: read-only confirmed
   ```

2. List the pages/databases that the integration is scoped to access:

   ```
   # Authorized Notion pages/databases:
   # - Offers (database)
   # - ICP Map (database)
   # - Claims Ledger (database)
   # - Hard Excludes (page)
   # - CTA Set (database)
   # - Voice Rules (page)
   ```

### Step 8: Invalidate the Old Token (Cleanup)

1. Return to the Notion integration console (Step 1).

2. In the **Secrets** or **API Tokens** section, confirm that the old token is no longer listed or is marked as **"revoked"** or **"inactive"**.

   **Note:** Notion automatically revokes the old token when you generate a new one. If the old token still appears as active, click **"Revoke"** or **"Delete"** to ensure it is disabled.

3. If you are decommissioning the integration entirely (not just rotating), click **"Delete integration"** or **"Disable"**. Any application using the old token will immediately receive 401 errors on the next API call.

### Step 9: Update Operational Records

1. In your run ledger or internal operational log, record:

   ```
   2026-08-06 | Notion internal integration token reissued
   Scope: READ-ONLY, fact-location pages only
   Health check: PASSED
   Brand-truth resolution test: PASSED
   Operator: [your name]
   ```

2. If your team maintains an operational calendar or audit log, mark this reissue complete.

---

## Failure Recovery

**If the token cannot be reissued or fails health check:**

- The run will automatically degrade to **research-only — knowledge base unavailable** per §6.2.
- The run digest will display: **"the knowledge-base integration token was rejected"** (exact message per §6.2), with no attempt to collect brand truth or enter generation stages.
- Media spending is prevented: research and ranking complete, but no media is generated and no text budget is spent beyond the (minimal) tokens used in brand-truth diagnosis itself.
- The operator review package will carry a plain statement of the cause and the fix: **"Notion token invalid. Reissue per runbook and retry."**
- **This is a safe failure.** Research output remains complete and reusable; the next run or an interactive re-run can immediately spin the same topics once the token is fixed.

---

## Troubleshooting Reference

| Symptom | Likely Cause | Fix |
|---|---|---|
| Health check returns 401 Unauthorized | Token is invalid, revoked, or not in secrets store | Regenerate token (Step 3), verify character-by-character (Step 4) |
| Health check passes, but brand-truth read fails with 403 | Token is valid but not scoped to the failing page/database | Return to Step 2, add the failing page/database to **Associated pages** |
| Health check or read returns 429 Too Many Requests | Rate limit reached (unlikely in health check, more likely in full read) | Wait 1 minute and retry. If persistent, contact Notion support or reduce request frequency |
| Brand-truth resolution reports MINIMAL or INSUFFICIENT band | Token is valid but brand truth is incomplete or stale | Check §6.2's degrade preconditions; verify claim ledger and offer catalogue are actually populated in Notion |
| Health check succeeds but brand-truth read timeout | Network latency or Notion API slowness | Retry. If persistent, check Notion's status page for service incidents |

---

## Related Sections

- **§17.2** — Phase 0 deliverables (token-reissue runbook requirement)
- **§6.2** — Brand-truth resolution, health checks, token scope and credential validity
- **W2-11** — Notion internal integration token is read-only, scoped to designated fact locations
- **R5-F3** — Notion token health check at run start and reissue runbook requirement
- **C1 §2** — Notion REST API (internal token) vs. MCP for unattended cron

---

## Checklist Before Reissue is Complete

- [ ] Workspace admin access confirmed (Step 1)
- [ ] Integration permissions reviewed and corrected (read-only, scoped to fact-location pages only) (Step 2)
- [ ] New token generated and copied (Step 3)
- [ ] New token stored in local secrets file/env var (Step 4)
- [ ] Health check passed with 200 OK (Step 5)
- [ ] Brand-truth resolution test passed (Step 6)
- [ ] Secrets metadata updated with reissue date and scope (Step 7)
- [ ] Old token revoked in Notion console (Step 8)
- [ ] Operational records updated (Step 9)
