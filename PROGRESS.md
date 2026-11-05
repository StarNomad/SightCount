# SightCount v1 — progress checkpoint (Nov 2, 2026, VM build)

## What works (tested)
- Server (Python stdlib only, no pip): `python3 server.py --port 8000`
  - `GET /api/health` -> `{"ok": true, "meta_api_key_set": false}` (live curl test, Nov 2)
  - `POST /api/interpret` with count=12/groups=3/spread=wide -> labelled LOCAL FALLBACK
    interpretation (live curl test, Nov 2)
  - `GET /` -> index page, HTTP 200, 2547 bytes; `app.js` HTTP 200 (live curl test, Nov 2)
- Meta API code path: `meta_client.py` posts OpenAI-compatible Chat Completions to
  https://api.meta.ai/v1/chat/completions, model muse-spark-1.3, key from
  META_MODEL_API_KEY env var only. Mock-tested, no network, no real key:
  - `python3 tests/test_meta_client.py` -> 3/3 PASS (fallback without key,
    real path with mock opener incl. auth header + api.meta.ai URL check,
    key never echoed in output, honest fallback labels)
- Frontend (static/index.html, app.js, style.css): one page with count +
  interpretation + event log; sample scene (synthetic, grid-placed figures that
  the blob counter counts exactly), webcam preview, image upload; every mode
  carries its honest label in the UI. JS syntax checked with node --check.
- README.md: Indie track, SENTINEL-EDGE disclosed as pre-existing (not the
  submission), run instructions, key setup, honest limits.

## What was NOT tested live (gaps, not hidden)
- Real Meta API call with a real key (no key on this VM). The path is present
  and mock-tested; one live run with a key is still needed before submission.
- Browser-side counting end-to-end (no live browser on this VM run): the JS
  blob counter is implemented and syntax-checked, but not clicked through in a
  real browser. Sample-scene counting logic (grid figures, min blob size 40px)
  is designed so drawn figures count exactly; verify in-browser before filming.
- Webcam path on a real device (needs a browser with camera permission).

## Still missing — Robert's steps
1. **API key**: create at dev.meta.ai, set META_MODEL_API_KEY, run once, confirm
   the badge flips to META MODEL API. Optionally claim the $150 credits by Nov 4.
2. **Demo video (3 min, event-built work only)**: record the app running —
   sample scene count + interpretation, and ideally a real camera frame.
3. **Public repo**: create on his own account (NOT from this VM login — the
   standing rule), push this folder, confirm it opens logged out.
4. **Submission form**: accept Official Rules, Indie track, teammates, link repo
   + demo video, submit by **Nov 4, 2026, 9:00 PM ET**.
5. **Discord join**: unconfirmed; workshops/credit forms live there, not a
   submission gate per prior record.

## Files
- server.py, meta_client.py, static/{index.html, app.js, style.css},
  tests/test_meta_client.py, README.md, PROGRESS.md (this file)
- No real credentials anywhere in the tree: the key is read from the
  environment only; the test uses a fake placeholder string, never a real key;
  the README shows the export command with no key value filled in.
