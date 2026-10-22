# TTN One video and grid style lock

Approved by Hector 2026-10-21. This replaces the old "rotate five looks across the week" rule (teal, white, black, notebook, photo covers) in ttn-visuals and ttn-content-week. Every reel, carousel cover and single image from now on follows this file. Picks come from the Reel Style Picker artifact (ratings saved there), the mock ups grid_final.png and video_design_final.png.

## The grid

- Base is notebook paper: cream #F6F1E4, ruled blue lines, red margin line on the left.
- Every 3rd post on the grid is the app's navy #0B0F19. Reels and carousels both count; stories don't. With 3 columns this keeps navy in one column as new posts push the grid along. Plan the posting order so the rhythm holds.
- Contrast rule (Hector, 2026-10-21): the app screen never matches the background. Dark mode screens go on paper. Notebook theme and light mode screens go on navy. Never a Notebook screen on paper.
- Same layout on every tile:
  - Label slot at the top: "PERSONAL TRAINERS," in Montserrat ExtraBold, or the series pill (Space Mono, teal, e.g. HOW TO 14) for series posts. The Series cover (V05) is the locked cover style.
  - Two line headline, Montserrat ExtraBold, one size across the grid; write headlines to fit two lines.
  - Second headline line in the accent: dark coral #B94D3F on paper (orange #EE7868 is 2.5 to 1 on paper and fails), normal orange #EE7868 on navy.
  - App screen or photo in the same spot below the headline, screen cropped close on the feature the post is about. Each post shows a different screen.
  - Lockup bottom left (icon in white circle + THE TRAINING NOTEBOOK ONE, ONE in orange), sized to read at grid size.
  - Swipe arrow bottom right on carousels (kept for the feed, even though the grid shows Instagram's own icon).
  - Handwriting (Kalam): at most one note per cover, 1 or 2 words, big enough to read at grid size, only on tiles where it points at the app, with a drawn arrow. Teal on paper, yellow #F5C84C on navy. Yellow is never text on paper.
  - Tape on photos only occasionally; otherwise a clean white border.
- Grid crop: posts are 1080 x 1350, the grid shows the middle 3:4. Everything that matters sits inside it.

## Reels on the grid

- Every reel gets a designed cover from the same tile template (notebook or navy by its place in the rhythm). The builder (reel2.py) opens each video on that cover, so Publer's default thumbnail is the cover. Never a random frame.
- The cover is 9:16; the grid shows the middle 3:4. All words, the phone and the logo sit inside that middle area; paper or navy continues above and below so it looks complete full screen.

## Inside the videos

- Type: Montserrat ExtraBold for headlines and captions. Space Mono for labels and the series bar. Kalam for handwriting.
- Color grade: one look on every clip, in color: slightly cooler shadows, natural warm skin, a little less saturation, a little more contrast. Black and white only as a deliberate effect (Black and white punch word pop).
- Position: words in the upper third (P03), always below the top safe line.
- End card (K05, fixed 2026-10-22 after Hector saw it cut off on Reels): "Try the 7 day / free trial" on two lines, every line at least 100 px in from each side (a full screen iPhone crops about 97 px a side), platforms read "App Store · Google Play · Browser". File: vt/endcard.png, template ttn_templates/endcard.html, copy in ttn-reels/tools/endcard. Videos 22 Oct to 6 Nov keep the old card by Hector's call.
- Safe zone (1080 x 1920): nothing above 14% from the top, nothing in the bottom 35%, 6% side margins, and nothing in the right 21% below 60% from the top (Instagram's buttons). Hector flagged safe zone on several looks; check every template against this notch.
- App screens follow the same contrast rule as the grid. Notebook backgrounds are fine behind dark mode screens only.

## Voice and mix

- Hector chose 5 Google Chirp 3 HD voices on 2026-10-21, replacing the Kokoro house voice: male Orus (his favorite), Algenib, Sadachbia; female Aoede, Laomedeia. Charon was dropped.
- All five rotate in this order, one per daily video: Orus, Aoede, Algenib, Laomedeia, Sadachbia. The schedule for 22 Oct to 6 Nov is in claude/CONTENT_LOG.md. Next up on 7 Nov: Aoede.
- Mix (fixed 2026-10-21 after Hector flagged loud music): each voice line levelled to -16 LUFS, music 19 dB under speech and 8 dB under in the gaps with 0.3 s ramps, final file -14 LUFS.

## Kept looks (codes from the Reel Style Picker)

Frame (in every video, keep tight):
- Words on screen: C01 One word punch, C07 Stacked title with teal bar, C11 Circled word. Maybe: C03 Teal box on the key word.
- Titles: T01 Series bar, T04 Handwritten note and arrow, T07 Sticky note.
- Word pops: CW03 Photo drop, CW04 Black and white punch. Pictures from free stock (Pexels, Unsplash) fetched through Hector's Chrome, saved to a word pops bank on HecSSD; 1 to 3 pops per 20 s video; no logos, famous people, or film and TV clips.
- Transitions: X04 Whip pan between footage shots, X09 Page turn into and out of the notebook. Nothing else.
- Cover: V05 Series cover.
- Position: P03 Upper third.

Tools (use when the content calls for them):
- Hooks: HK01 Start mid action, HK03 Wrong way right way, HK05 Number slam, HK06 Phone drop, HK07 Client text, HK09 Open loop. Don't open two videos in a row with the same hook.
- Numbers and boards: N01 Big counter, N02 Progress line, N03 Last time vs today, N04 Numbered board, N05 Two column compare, N06 Four into one, N07 Stopwatch, N08 Checklist ticks, N09 Calendar flip, N11 Star rating.
- Showing the app: S01 Phone rises in, S03 Spotlight, S05 Two phones, S07 Drawn on circle and arrow.
- Full screen cards: K01 Black statement, K02 Teal statement, K04 Question card, K05 End card (same on every video), K06 DONE stamp. Maybe: K03 Word stack.
- Sounds: whoosh, tap, bass hit, swipe, phone buzz, message ping, keyboard typing, error buzzer, success chime, clock tick. Final files from free libraries matched to these.

Dropped (don't use): freeze frame, question to the trainer hook, punch in on the face, sentence builds, orange brackets, word lights up, plain subtitles, yellow bar title, side words, name tag, viewfinder, full frame flash, sticker pop, icon pop, top third slide, taped photo pop, tap and zoom, outline and label, full screen with label, flash frame, zoom punch, circle reveal, teal wipe, hard cut as a style, and the other new transitions.

## Captions

- Every caption on every network opens with "Personal trainers," and carries "Try the 7 day free trial".
- Instagram and TikTok: "Link in bio." plus #personaltrainer #fitnesscoach #ptlife #trainertips. Every other network: the site link with utm_source set to that network, utm_medium=social, utm_campaign=organic.
- Copy follows FACTS.md (rev 6): the main screen is "Home", never "Dashboard"; no "saved" or "safe" wording, even for a button (say "tap Save").

## Fonts
Headline Montserrat ExtraBold (Anton was a maybe). Labels Space Mono (replaces JetBrains Mono). Handwriting Kalam (replaces Caveat).

## Open
- Picker notes still to apply in the templates: HK03 top text a touch close to the safe line; HK01 check every look against the button notch.
- Every post scheduled from 21 Oct 9 PM to 6 Nov is in this style (rebuilt 2026-10-21, audited 2026-10-22).
