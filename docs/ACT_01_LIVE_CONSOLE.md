# Act 01 · Live Vesper Console

The interview console is a projection layer over the existing local DIO Presence Core. It does not become an authority source.

## Sequence

1. Browser checks DIO Presence health.
2. Human speaks or types a business request.
3. Browser sends text to the local demo server.
4. Demo server constructs a signed public webchat envelope.
5. DIO Presence performs its real classification, routing, intake, LINGUA and authority work.
6. The browser renders the returned decision and authority receipt.
7. Only the exact returned Vesper reply text is offered to the configured Pocket TTS voice.
8. Audio is played locally. Voice rendering does not create send or execution authority.

## Safety

- Localhost by default.
- No Telegram switch is enabled.
- No payment or fulfilment rail is enabled.
- No attachment parsing is added.
- SAFE STOP prevents further UI submissions.
- Speech recognition is browser-dependent and is an input convenience only.
- If Vera Pocket is not configured or Pocket TTS is unavailable, text remains canonical and the UI reports voice unavailable.

## Termux

Run DIO Presence separately on 127.0.0.1:8787 with a throwaway 32+ character public signing secret. Export the identical secret in the demo shell.

The canonical DIO snapshot already declares Vera Pocket as the approved default public profile. Select it explicitly for the demo:

    export DIO_VESPER_VOICE_PROFILE='vera_pocket_public'

If Pocket TTS is not on its default 127.0.0.1:8000 endpoint, set:

    export DIO_VESPER_POCKET_TTS_URL='http://127.0.0.1:<port>'

Then:

    python scripts/serve_demo.py

Open http://127.0.0.1:8765 in the phone browser.

Do not invent a profile id. Inspect DIO config/vesper_voice_profiles.json and use the existing Pocket TTS entry.