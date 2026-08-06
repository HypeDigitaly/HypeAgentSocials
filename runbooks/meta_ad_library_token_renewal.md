# Meta Ad Library API Token Renewal Runbook

**When to use this:** Meta Ad Library API token is expiring within the renewal window, has expired, or fails at run time with an authentication error.

Written 2026-08-06, governed by ARCHITECTURE_PLAN.md §17.2, §6.2 (R5-F3), and C1 §2.

---

## Blast Radius

This token gates **one research axis only** — the ad-library collection source. A failed or expired token degrades that single source, and the run continues as **partial-success — degraded sources**, with all other research paths intact. No spend is affected.

---

## Trigger Conditions

The token renewal workflow is triggered by any of the following:

1. **Pre-expiry renewal window:** The token's recorded expiry date is within 14 days of today. Check the date recorded during last issuance (stored in secrets file metadata and in dated copy of API terms per §17.2).

2. **Run-time authentication failure:** A collection run attempts to pull from Meta Ad Library and receives a 401 Unauthorized or "invalid token" error. This is logged with timestamp in the run digest under the ad-library source panel.

3. **Planned rotation:** The operator has decided to rotate credentials as part of routine security practice (e.g., quarterly, or after a known personnel change).

---

## Step-by-Step Renewal Process

### Step 1: Verify Your Identity (One Time per Renewal Session)

The Meta Ad Library API requires personal government-ID verification tied to your account. This verification was completed during initial setup per §17.2.

- Ensure you have your government-issued photo ID (passport or national identity card) and a device with a camera.
- Have the email address associated with your Meta business account ready.

**[TO CONFIRM AT FIRST ISSUANCE]** Access the Meta Ad Library API settings interface at: [exact URL path and UI flow].

### Step 2: Initiate Token Renewal in Meta's Console

1. Log in to your Meta business account with the verified identity.
2. Navigate to [TO CONFIRM AT FIRST ISSUANCE] **Settings → Integrations → API Tools → Ad Library**.
3. Locate the existing token entry (labeled with the date it was issued).
4. Click **"Regenerate Token"** or **"Request New Token"** (exact button label: [TO CONFIRM AT FIRST ISSUANCE]).
5. Meta will present the new token value (a long string, typically beginning with [TO CONFIRM AT FIRST ISSUANCE]). **Copy this value immediately — it is shown only once.**
6. Note the **expiry date** shown on the same screen. This date will be required in Step 4 below.

### Step 3: Store the New Token in the Local Secret Store

**Never commit the token to the repository or any version-controlled file.**

1. Open your local secrets file or environment variable store (the location and mechanism were established during initial setup per §6.2):
   - **If environment variable:** Export as `META_AD_LIBRARY_TOKEN="<new_token_value>"`
   - **If local secrets file:** Update the entry with key `meta.ad_library_token` with the new token value.
   - **If Windows credential vault:** [TO CONFIRM AT FIRST ISSUANCE] [exact instructions].

2. Save and verify the secret store is readable by the application. A quick test: run `echo $META_AD_LIBRARY_TOKEN` (Unix) or `$env:META_AD_LIBRARY_TOKEN` (PowerShell) and confirm the token is present (output may be truncated).

### Step 4: Record the New Expiry Date

**Location:** In the **secrets-metadata** file or comment block alongside your secrets (never the token itself, only the metadata).

Add or update the following line with the expiry date from Step 2:

```
# Meta Ad Library API Token
# Renewed: 2026-08-06
# Expiry: [DATE FROM STEP 2]
# API Terms Accepted: [DATE FROM STEP 5 BELOW]
```

Example:
```
# Meta Ad Library API Token
# Renewed: 2026-08-06
# Expiry: 2027-08-06
# API Terms Accepted: 2026-08-06
```

### Step 5: Download and Store the Accepted API Terms

1. In Meta's console (same page from Step 2), locate and download the current **API Terms of Service** or **Platform Policy Agreement** document. The file will typically be named `Meta_Ad_Library_API_Terms_[DATE].pdf` or similar.

2. Save this dated PDF to a **non-version-controlled, operator-accessible location** (recommendation: a shared folder on your team's file storage with read/execute only access):
   - **Suggested path:** `C:\Users\[YourName]\Shared\Meta_API_Terms\Meta_Ad_Library_API_Terms_2026-08-06.pdf` (Windows)
   - **Or:** `/Users/[YourName]/Shared/Meta_API_Terms/Meta_Ad_Library_API_Terms_2026-08-06.pdf` (macOS/Linux)

3. In your secrets metadata file, record the path and date:
   ```
   # API Terms Accepted: 2026-08-06
   # Terms document: C:\Users\[YourName]\Shared\Meta_API_Terms\Meta_Ad_Library_API_Terms_2026-08-06.pdf
   ```

**Why:** The accepted terms are required proof per §17.2 that access is conditioned on both identity verification and agreed terms. Keeping a dated copy allows you to prove compliance if questioned later.

### Step 6: Test the New Token

Before running a full pack collection, verify the token works:

1. Run a **test collection** limited to the ad-library source only (if your app supports a source filter) or run a minimal **research-only mode** pack to exercise the ad-library collection path.

2. Monitor the run output for the ad-library source panel. You should see:
   - ✓ **Status: collected successfully**
   - ✓ **Records pulled:** [number]
   - ✓ **Timestamp:** [current run date/time]

3. **If the test fails** with a 401 error: Stop. The token was not correctly stored or has not yet propagated through Meta's systems (rare, but give it 5–10 minutes and retry). Return to Step 3 and verify the token value character-for-character. If still failing after 15 minutes, escalate: the token generation may have failed on Meta's side — return to Step 2 and request a new token, then start again at Step 3.

### Step 7: Update Run Logs and Documentation

Once the test passes:

1. In your run ledger or internal operational log, record:
   ```
   2026-08-06 | Meta Ad Library token renewed
   Expiry: 2027-08-06
   Test run: SUCCESS
   Operator: [your name]
   ```

2. If your team maintains an operational calendar or checklist, mark this renewal complete so the next scheduled renewal (14 days before expiry, i.e., 2027-07-23) is visible.

---

## Failure Recovery

**If the token cannot be renewed:**

- The ad-library source will fail on the next collection attempt with a specific error in the run digest: **"Ad Library API: authentication rejected"** or **"Ad Library API: invalid token"**.
- Per §17.2 and §6.2, this produces a **degraded-source** outcome: all other research sources continue, and the run completes as **partial-success — degraded sources**. No media spend is affected.
- The operator review package will carry a **degraded-source banner** naming the ad-library axis and explaining that competitor creative insight from Meta's ad library is not available for this run.
- **No manual intervention is required to proceed;** the operator may review and publish from the other research sources.

---

## Related Sections

- **§17.2** — Phase 0 deliverables (token-renewal runbook requirement, W2-15)
- **§6.2** — Brand-truth resolution and credential health checks
- **R5-F3** — Notion token health check at run start + reissue runbook
- **C1 §2** — Notion vs. Meta API integration choices

---

## Checklist Before Renewal is Complete

- [ ] New token copied from Meta console (Step 2)
- [ ] New token stored in local secrets file/env var (Step 3)
- [ ] Expiry date recorded in secrets metadata (Step 4)
- [ ] Dated API terms PDF downloaded and stored (Step 5)
- [ ] Test collection run passed with new token (Step 6)
- [ ] Renewal logged in operational records (Step 7)
