# Mudras social designs: posts #1–#2 (23 Oct 2026)

| # | Platform | Files | Photos (Unsplash License, free for commercial use) |
|---|----------|-------|---------------------------------------------------|
| 1 | Instagram carousel (4 slides) + Story | `post-01-instagram/` | Slides 1 + Story: https://unsplash.com/photos/Z-GDQeDaSB4 (cropped to legs, bib years cut). Slide 4: https://unsplash.com/photos/gavoj4Q_C_Q (top cropped so no face shows). |
| 2 | Facebook feed 1080×1350 + link image 1200×630 | `post-02-facebook/` | https://unsplash.com/photos/yBLLzNcA6GU |

The updated calendar is `Mudras_Social_Calendar_23Oct-5Nov_2026Posts_56.csv`. For rows 1–2, the status is now
"Design ready - pending client approval". The sheet's original photos (a calendar, and a towel-and-bottle still life) did not match the copy, so they were replaced. *Image description*, *Image source link* and *Direct download* now describe the new photos.

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

## Client guidelines for all posts (keep following these)
- Use the exact logo from mudras.com, and only the website's fonts and palette: black, gold `#F0CC75` and white, with black-and-white photos. Do not use new panel colours (for example green or cream).
- Follow the layouts of the brand's own posts (the reference images from @mudrasmassage), and vary them so posts don't all look the same.
- **No faces** in stock photos. Faces are fine in photos from the client's own website.
- **No equipment in images:** no massage guns, scraping tools or other devices. Show hands-on work only.
- Every image must match its post text. Don't reuse a photo that has already been posted.
- Use only royalty-free (Unsplash) or client-website images, and record every image link in the post's md file.
- Name files with the platform and dimensions, for example `instagram-feed-1080x1350.png`.
- Check every image for size, safe zone, at most 2 fonts, at most 7 words per line, contrast of at least 4.5:1, and text under 20% of a Facebook image.
- No emoji or step numbering on images unless the client asks for them.
