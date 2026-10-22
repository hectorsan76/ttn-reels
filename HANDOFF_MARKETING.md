# Marketing handoff · updated 2026-10-22 18:20 WITA

Read first: FACTS.md (rev 6), claude/VIDEO_AND_GRID_STYLE_LOCK.md, claude/CONTENT_LOG.md, COPY-VOICE-TTN.md.

## Where things stand
- Social is fully scheduled 22 Oct to 6 Nov in Publer (workspace "The Training Notebook One"): every day a video at 9 AM Bali on 7 networks and a carousel at 9 PM Bali on 6 networks, plus Instagram photo Stories at 9:15 AM and 9:15 PM (30 total). YouTube Posts tab: one per day at 9 PM, done in Hector's Chrome, all 16 scheduled. Every caption audited on 22 Oct against FACTS rev 6 and the style lock; every video about -14 LUFS.
- Videos 22 Oct to 6 Nov keep the old end card (Hector's call). The new end card (vt/endcard.png) is the default for everything from 7 Nov.
- Profiles on all 7 networks were redone on 22 Oct (names, bios, links with utm, avatar, X and LinkedIn banners, YouTube description and trailer). Hector did the phone-only items himself (Instagram highlights, link order, pinned posts). Facebook avatar still the old one.
- Tools: everything needed to render is in GitHub hectorsan76/ttn-reels › workbench (README there has the restore lines). Carousel specs in workbench/templates/posts, video configs in workbench/vt/cfg. Story images in ttn-reels/stories.

## App update (reported by the app thread 22 Oct 18:10)
- Live: Google Play and web 0.5.3 (43). App Store 0.5.2 (42), 0.5.3 in Apple review since 22 Oct 09:15. Build 44 next, no date; it only changes the empty new workout page, so never shoot an empty new workout.
- Changed screens: Home ("Needs a look" is now "Follow up", amber reasons such as "Not done · yesterday", quiet day "Everyone's on track"; Done tick on finished workouts in the Today card), Program templates (switch "My templates" / "TTN One programs", goal and level chips, TTN One badge), new read only TTN One program page, own program page header. Everything else unchanged since 0.5.1.
- New screenshots: HecSSD › TTN Reels › 00 App screens › 2026-10-22, 30 PNG (15 screens × Dark and Notebook, iPhone 6.9 inch, 1320 × 2868, only the five demo clients). Cautions: use photo_compare_dark only; prefer client_list over client_profile; calendar_week over calendar_day.

## Owner decisions waiting (collected, none pressed)
1. FACTS rev 7, line by line: store versions; "Follow up" replaces "Needs a look"; the 20 TTN One programs (switch, filters, read only page, Add to my templates, Apply to a client, three languages); moved exercises show the original numbers as a grey line. Until he says yes, the 20 programs and "Follow up" stay out of copy. Planner advice: approve the programs for copy once Apple approves 0.5.3, so iPhone trainers see what the post shows.
2. Swap the old Home screenshot in the 25 Oct carousel (d25_walkin) and 31 Oct carousel (d31_twotaps) for the new home screen: about 1 h. Covers r17p, r02p, r03n, r21p and client screens in d24, d30, n04 still show older screens of unchanged layouts, leave them.
3. Older: Facebook avatar; make the old YouTube tutorials unlisted; video 16 (custom demo link).

## Next up
1. 7 Nov onward content batch in the style lock, using the new screens (about 6 to 8 h). Voice rotation continues with Aoede on 7 Nov. Hector screen records any new flows on his phone (about 10 min); the 20 TTN One programs are the obvious new how-to once approved.
2. Store screenshots: the new Home and Program templates make the App Store and Play strips stale (ttn-store-assets skill).
3. Website FAQ fixes (ttn-website-change); copy-gate skill still lists Sports Club LA.

## Publer notes
- Account ids and working tricks are in claude/CONTENT_LOG.md. Pull a post with change_publer_post_state to draft_private (needs Hector's chat yes). Media edits on scheduled posts do not stick: recreate the post. Dedupe list results by id.
