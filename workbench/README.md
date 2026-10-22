# Workbench (backup of the cloud tools, 2026-10-22)

Restore in a fresh session, from the folder that holds ttn-reels:

    cp -r ttn-reels/workbench/templates ~/ttn_templates    # carousel, cover, banner, end card (Playwright + PIL)
    cp -r ttn-reels/workbench/vt ~/vt                      # reel2.py video builder, cfg/, fonts, sfx, end card
    pip install --break-system-packages playwright pillow soundfile

- Carousels: python3 ~/ttn_templates/render_post.py ~/ttn_templates/posts/<post>.json <out_dir>
- Videos: python3 ~/vt/reel2.py ~/vt/cfg/<video>.json (reads raw clips from the staged
  "TTN Reels" folder; the Google TTS key is read from the staged
  "04 Working files/video_tools/google_tts_key.txt", never copied here).
- New end card is vt/endcard.png (template templates/endcard.html).
- yt_captions/: YouTube Posts captions 22 Oct to 6 Nov. profile_assets/: avatar and banners.
- App screens 0.5.3 (43): HecSSD > TTN Reels > 00 App screens > 2026-10-22 (30 PNG).
