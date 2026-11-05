# SightCount v1 — Meta Global AI Developer Hackathon

**Track: Indie Developer. Submission deadline: Nov 4, 2026, 9:00 PM ET.**

## What it does

SightCount is real-time audience intelligence from any camera, in one web page:

1. **Count** — a camera feed, an uploaded image, or a labelled synthetic sample
   scene. Counting is a simple connected-blob counter in the browser.
2. **Interpret (the Meta layer, not a plain counter)** — the measured scene
   (count, clusters, spread) is sent to the Meta Model API (Muse Spark) for a
   scene interpretation: crowd mood, attention, grouping, what is happening.
   A plain counter/dashboard is explicitly discouraged by the hackathon, and
   this layer is what makes SightCount more than one.
3. **Event log** — every count and interpretation, timestamped, on the same page.

## Disclosure: SENTINEL-EDGE is pre-existing work

SENTINEL-EDGE (a prior, separate project) is **disclosed as pre-existing work
and is NOT this submission**. SightCount v1 was built fresh as new event work
for this hackathon (Nov 2, 2026, on this VM). Nothing from SENTINEL-EDGE's
code is reused here; this app is a new, small, standalone build.

## How to run it

No pip installs. Python 3 standard library only.

```bash
cd ~/workspace/meta-hackathon/sightcount
python3 server.py --port 8000
# open http://127.0.0.1:8000/ in a browser
```

## How to set the API key (Meta Model API)

```bash
# Set this to the key you create at dev.meta.ai (paste your own key here):
export META_MODEL_API_KEY
export META_MODEL_NAME="muse-spark-1.3"          # optional, this is the default
export META_MODEL_API_BASE="https://api.meta.ai/v1"  # optional, this is the default
python3 server.py --port 8000
```

The key is read only from the environment, never hardcoded, never committed,
never logged. Without a key the app still runs and the interpretation badge
reads **LOCAL FALLBACK** — the UI never pretends a fallback is a Meta result.
With a key, the badge reads **META MODEL API (muse-spark-1.3)**.
The $150 Meta Model API credits (claim by Nov 4) are the intended funding
for live calls; claiming them is Robert's account step.

## Honest limits (read before judging or submitting)

- **The counter is a blob counter, not a person detector.** It counts
  connected dark regions in a frame. On real camera footage it is an estimate,
  not a verified headcount. The UI says this on the page itself.
- **Sample mode is synthetic.** It draws computer-generated figures on a
  canvas; its count is a count of drawn figures, labelled as demo/sample mode.
  It is never presented as real detection.
- **The Meta API path is code-complete and mock-tested, but NOT live-tested**,
  because no API key was available on this VM at build time. Before submission,
  run it once with a real key and confirm the interpretation badge flips to
  META MODEL API.
- **No demo video, no public repo, no submission form yet** — those are
  Robert's remaining steps (see PROGRESS.md). Nothing has been published.
- Built on the VM only; Nova (Dell 5441) was powered off during this build.
