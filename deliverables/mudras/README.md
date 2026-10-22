# Mudras social designs: posts #1–#2 (23 Oct 2026)

| # | Platform | Files | Photo (Unsplash License) |
|---|----------|-------|--------------------------|
| 1 | Instagram carousel (4 slides) + Story | `post-01-instagram/` | https://unsplash.com/photos/bwOAixLG0uc |
| 2 | Facebook feed 1080×1350 + link image 1200×630 | `post-02-facebook/` | https://unsplash.com/photos/VxAwTeiqDao |

The updated calendar is `Mudras_Social_Calendar_23Oct-5Nov_2026Posts_56.csv`. For rows 1–2, the status is now
"Design ready - pending client approval", and *Direct download* holds the image file URLs.

## Brand sources (from mudras.com)
- Logo: the header logo from mudras.com (`source/site/orig_Group_1487669750.png`, 344×101, the largest size the site serves).
- Colors come from the site theme: gold `#F0CC75`, black `#212121`, white `#FFFCF2`.
- Fonts:
  - Body: Raleway (the site's body font).
  - Headings: the site uses **orpheus-pro**, which is an Adobe Fonts licence we don't hold, so the headings use **Bellefair** (Google Fonts, free) as the closest match. Swap it in `source/design/posts.html` if orpheus-pro is available.
- The art direction follows @mudrasmassage feed posts: black-and-white photos, a gold logo, white serif copy and thin gold rules.

## Design rules checked (`source/tools/qa.js` + `qa.py`)
Each image was checked for:
- exact size
- the central 80% safe zone (Story keeps clear of the top 250px and the bottom 340px)
- at most 2 fonts
- a 16px minimum font size
- at most 7 words per line
- one bottom-right CTA at least 44px tall
- text contrast of at least 4.5:1
- text covering under 20% of the Facebook image

All 7 images pass. There are no faces in any image.

The Story leaves y 460–980 clear for Instagram's native countdown sticker (to 1 Nov).
