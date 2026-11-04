"""SEO checks: turn a finished crawl into a list of issues, each with why it matters and how to fix it.

Every check writes rows (code, url, detail) into the crawl's issues table. CHECKS
describes each code in English and Hindi for the dashboard.
"""

import json
from collections import defaultdict
from urllib.parse import urlsplit

from crawler import normalize

# code: (severity, category, title, title_hi, why + fix, why + fix in Hindi)
CHECKS = {
    # ---- response codes
    "client_error": ("error", "Response", "Pages returning 4xx (not found / forbidden)",
                     "4xx वाले पेज (नहीं मिला / मना)",
                     "Visitors and Google hit a dead end. Fix the page, or 301-redirect it to the closest working page and update links pointing to it.",
                     "विज़िटर और Google को खाली पेज मिलता है। पेज ठीक करें, या 301 redirect से सबसे मिलते-जुलते पेज पर भेजें और उस पर आने वाले लिंक बदलें।"),
    "server_error": ("error", "Response", "Pages returning 5xx (server error)", "5xx वाले पेज (सर्वर गड़बड़ी)",
                     "The server failed. Google lowers crawling of sites that error often. Check server logs, hosting limits and plugins.",
                     "सर्वर फेल हुआ। बार-बार ऐसा हो तो Google साइट कम क्रॉल करता है। सर्वर लॉग, होस्टिंग लिमिट और प्लगइन देखें।"),
    "no_response": ("error", "Response", "No response (timeout / connection failed)", "जवाब नहीं मिला (टाइमआउट / कनेक्शन फेल)",
                    "The page didn't answer in time. Check if it is very slow or blocked by a firewall/CDN for bots.",
                    "पेज ने समय पर जवाब नहीं दिया। देखें कि पेज बहुत धीमा है या फ़ायरवॉल/CDN बॉट्स को रोक रहा है।"),
    "blocked_robots": ("notice", "Response", "Blocked by robots.txt", "robots.txt से ब्लॉक",
                       "Search engines won't crawl these. Fine for private areas; make sure no important page is blocked.",
                       "सर्च इंजन इन्हें क्रॉल नहीं करेंगे। प्राइवेट हिस्सों के लिए ठीक है; ध्यान रखें कि कोई ज़रूरी पेज ब्लॉक न हो।"),
    "robots_unreachable": ("warning", "Response", "robots.txt could not be read", "robots.txt पढ़ा नहीं जा सका",
                           "The crawl went ahead without the site's robots.txt rules. Google pauses crawling when robots.txt errors, so fix the server or file.",
                           "क्रॉल robots.txt के नियमों के बिना हुआ। robots.txt में गड़बड़ी हो तो Google क्रॉल रोक देता है, सर्वर या फ़ाइल ठीक करें।"),
    "js_content": ("warning", "JavaScript", "Content or links appear only after JavaScript", "कंटेंट या लिंक सिर्फ़ JavaScript के बाद दिखते हैं",
                   "Google renders JavaScript later and less often, and AI crawlers (ChatGPT, Claude, Perplexity) don't run it at all, so they miss this content. Use server-side rendering or static HTML for the main text and links.",
                   "Google JavaScript देर से और कम बार चलाता है, और AI क्रॉलर (ChatGPT, Claude, Perplexity) इसे बिल्कुल नहीं चलाते, इसलिए यह कंटेंट उन्हें नहीं दिखता। मुख्य टेक्स्ट और लिंक के लिए server-side rendering या static HTML इस्तेमाल करें।"),
    "render_failed": ("warning", "JavaScript", "Page failed to render in the browser", "पेज ब्राउज़र में render नहीं हुआ",
                      "The page errored or hung while its JavaScript ran, so it was checked from raw HTML. Open it in a browser and check the console for errors.",
                      "JavaScript चलते समय पेज में गड़बड़ी हुई या अटक गया, इसलिए raw HTML से जाँचा गया। ब्राउज़र में खोलकर console की गड़बड़ियाँ देखें।"),
    "render_unavailable": ("warning", "JavaScript", "JavaScript rendering could not start", "JavaScript rendering शुरू नहीं हुई",
                           "No usable browser was found, so pages were checked from raw HTML only. Install Google Chrome or Microsoft Edge and crawl again.",
                           "कोई ब्राउज़र नहीं मिला, इसलिए पेज सिर्फ़ raw HTML से जाँचे गए। Google Chrome या Microsoft Edge इंस्टॉल करके दोबारा क्रॉल करें।"),
    "slow_page": ("warning", "Response", "Slow pages (over 1.5 s to respond)", "धीमे पेज (1.5 सेकंड से ज़्यादा)",
                  "Slow pages lose visitors and rankings. Use caching, a CDN, smaller images and fewer heavy plugins.",
                  "धीमे पेज से विज़िटर और रैंकिंग दोनों घटते हैं। कैशिंग, CDN, छोटी इमेज और कम भारी प्लगइन इस्तेमाल करें।"),
    "http_url": ("warning", "Security", "Insecure http:// URLs on an https site", "https साइट पर http:// वाले URL",
                 "Use https everywhere. Update the links and 301-redirect http to https.",
                 "हर जगह https इस्तेमाल करें। लिंक बदलें और http को https पर 301 redirect करें।"),
    # ---- redirects
    "link_to_redirect": ("warning", "Redirects", "Internal links pointing to redirects", "redirect पर जाने वाले अंदरूनी लिंक",
                         "Each redirect wastes crawl budget and a little speed. Change the link to point straight to the final URL.",
                         "हर redirect क्रॉल बजट और स्पीड बर्बाद करता है। लिंक को सीधे आख़िरी URL पर बदलें।"),
    "redirect_chain": ("warning", "Redirects", "Redirect chains (2+ hops)", "redirect की लंबी चेन (2+ हॉप)",
                       "A → B → C loses ranking signals and speed. Redirect A straight to C.",
                       "A → B → C से रैंकिंग और स्पीड घटती है। A को सीधे C पर redirect करें।"),
    "redirect_loop": ("error", "Redirects", "Redirect loops", "redirect लूप",
                      "The URL redirects back to itself and never loads. Fix the redirect rules.",
                      "URL घूम-फिर कर अपने ऊपर ही लौटता है और कभी नहीं खुलता। redirect नियम ठीक करें।"),
    # ---- links
    "broken_internal_link": ("error", "Links", "Broken internal links", "टूटे अंदरूनी लिंक",
                             "Links on your pages lead to missing pages. Update or remove each link (the page shown is where the link is).",
                             "आपके पेज के लिंक गायब पेज पर ले जाते हैं। हर लिंक बदलें या हटाएँ (दिखाया गया पेज वह है जिस पर लिंक है)।"),
    "broken_external_link": ("warning", "Links", "Broken external links", "टूटे बाहरी लिंक",
                             "Links to other sites that no longer work. Replace them with a working source or remove them.",
                             "दूसरी साइटों के लिंक जो अब काम नहीं करते। चालू लिंक लगाएँ या हटाएँ।"),
    "no_outlinks": ("warning", "Links", "Pages with no internal links out", "जिन पेज से कोई अंदरूनी लिंक नहीं",
                    "Dead-end pages trap visitors and crawlers. Link to related pages.",
                    "ये पेज आगे कहीं नहीं ले जाते। मिलते-जुलते पेजों के लिंक जोड़ें।"),
    "nofollow_internal": ("notice", "Links", "Internal links marked nofollow", "nofollow वाले अंदरूनी लिंक",
                          "nofollow on your own links stops ranking signals flowing. Remove it unless intended.",
                          "अपने ही लिंक पर nofollow से रैंकिंग सिग्नल रुकते हैं। ज़रूरत न हो तो हटाएँ।"),
    "orphan_page": ("warning", "Links", "Orphan pages (in sitemap, no links to them)", "अनाथ पेज (sitemap में हैं, पर कोई लिंक नहीं)",
                    "No page links here, so Google sees them as unimportant. Link to them from relevant pages or menus.",
                    "किसी पेज से इन पर लिंक नहीं, इसलिए Google इन्हें कम ज़रूरी मानता है। सही पेज या मेन्यू से लिंक करें।"),
    "deep_page": ("notice", "Links", "Deep pages (more than 3 clicks from home)", "गहरे पेज (होम से 3 से ज़्यादा क्लिक)",
                  "Pages far from the home page get crawled and ranked less. Link important ones from higher up.",
                  "होम से दूर के पेज कम क्रॉल और रैंक होते हैं। ज़रूरी पेजों को ऊपर के पेज से लिंक करें।"),
    # ---- titles
    "title_missing": ("error", "Titles", "Missing page title", "पेज टाइटल नहीं है",
                      "The title is the blue headline in Google results. Add a unique, descriptive <title> (50–60 characters).",
                      "टाइटल Google रिज़ल्ट की नीली हेडलाइन है। हर पेज पर अलग, साफ़ <title> लिखें (50–60 अक्षर)।"),
    "title_duplicate": ("warning", "Titles", "Duplicate titles", "एक जैसे टाइटल",
                        "Several pages share one title, so Google can't tell them apart. Make each title unique.",
                        "कई पेजों का टाइटल एक है, Google उनमें फ़र्क नहीं कर पाता। हर टाइटल अलग बनाएँ।"),
    "title_long": ("warning", "Titles", "Title too long (over 60 characters)", "टाइटल बहुत लंबा (60 अक्षर से ज़्यादा)",
                   "Google cuts it off with '...'. Put the important words first and shorten it.",
                   "Google इसे '...' से काट देता है। ज़रूरी शब्द पहले लिखें और छोटा करें।"),
    "title_short": ("notice", "Titles", "Title too short (under 30 characters)", "टाइटल बहुत छोटा (30 अक्षर से कम)",
                    "A short title misses keywords. Describe the page more fully.",
                    "छोटे टाइटल में कीवर्ड छूट जाते हैं। पेज के बारे में थोड़ा ज़्यादा लिखें।"),
    "title_multiple": ("warning", "Titles", "More than one <title>", "एक से ज़्यादा <title>",
                       "Keep exactly one title tag in <head>.", "<head> में सिर्फ़ एक title टैग रखें।"),
    # ---- descriptions
    "desc_missing": ("warning", "Meta description", "Missing meta description", "meta description नहीं है",
                     "Google then picks random text for the snippet. Write a 120–160 character summary that invites the click.",
                     "तब Google कोई भी टेक्स्ट दिखा देता है। 120–160 अक्षर का ऐसा सार लिखें जो क्लिक करने को मन करे।"),
    "desc_duplicate": ("warning", "Meta description", "Duplicate meta descriptions", "एक जैसे meta description",
                       "Write a unique description for each page.", "हर पेज के लिए अलग description लिखें।"),
    "desc_long": ("notice", "Meta description", "Meta description too long (over 160)", "meta description बहुत लंबा (160 से ज़्यादा)",
                  "It gets cut off in results. Keep it under about 160 characters.", "रिज़ल्ट में कट जाता है। लगभग 160 अक्षर से कम रखें।"),
    "desc_short": ("notice", "Meta description", "Meta description too short (under 70)", "meta description बहुत छोटा (70 से कम)",
                   "Use the space to sell the page.", "जगह का इस्तेमाल करके पेज के बारे में अच्छे से बताएँ।"),
    "desc_multiple": ("warning", "Meta description", "More than one meta description", "एक से ज़्यादा meta description",
                      "Keep exactly one.", "सिर्फ़ एक रखें।"),
    # ---- headings
    "h1_missing": ("warning", "Headings", "Missing H1", "H1 नहीं है",
                   "The H1 is the page's main heading. Add one that matches what the page is about.",
                   "H1 पेज की मुख्य हेडिंग है। पेज के विषय से मेल खाती एक H1 जोड़ें।"),
    "h1_multiple": ("notice", "Headings", "More than one H1", "एक से ज़्यादा H1",
                    "Usually keep one main H1 and use H2/H3 for sections.", "आम तौर पर एक मुख्य H1 रखें, बाकी के लिए H2/H3।"),
    "h1_duplicate": ("notice", "Headings", "Duplicate H1s", "एक जैसी H1",
                     "Several pages share the same H1. Make each one specific.", "कई पेजों की H1 एक है। हर एक को खास बनाएँ।"),
    "h2_missing": ("notice", "Headings", "No H2 subheadings", "कोई H2 सब-हेडिंग नहीं",
                   "Subheadings make long pages easier to read and understand.", "सब-हेडिंग से लंबे पेज पढ़ना और समझना आसान होता है।"),
    # ---- content
    "thin_content": ("warning", "Content", "Thin content (under 200 words)", "कम कंटेंट (200 शब्द से कम)",
                     "Very short pages rarely rank. Add useful detail, or merge them into a stronger page.",
                     "बहुत छोटे पेज कम रैंक होते हैं। काम की जानकारी जोड़ें या किसी मज़बूत पेज में मिला दें।"),
    "duplicate_content": ("warning", "Content", "Exact duplicate pages", "बिल्कुल एक जैसे पेज",
                          "Same text on several URLs splits ranking. Keep one and add a canonical or 301 for the others.",
                          "कई URL पर वही टेक्स्ट रैंकिंग बाँट देता है। एक रखें, बाकी पर canonical या 301 लगाएँ।"),
    "near_duplicate": ("notice", "Content", "Near-duplicate pages (very similar text)", "लगभग एक जैसे पेज",
                       "Pages that are almost the same compete with each other. Make them different or combine them.",
                       "लगभग एक जैसे पेज आपस में मुकाबला करते हैं। इन्हें अलग बनाएँ या एक कर दें।"),
    # ---- canonicals & indexing
    "canonical_missing": ("notice", "Indexing", "No canonical tag", "canonical टैग नहीं है",
                          "A self-referencing canonical tells Google which URL is the main one (helps with ?parameters).",
                          "खुद की ओर canonical बताता है कि मुख्य URL कौन-सा है (?parameter वाले URL में मदद करता है)।"),
    "canonicalised": ("notice", "Indexing", "Canonical points to another URL", "canonical किसी दूसरे URL पर",
                      "These pages ask Google to index another URL instead. Correct if intended.",
                      "ये पेज Google से किसी दूसरे URL को index करने को कहते हैं। जानबूझकर है तो ठीक है।"),
    "canonical_broken": ("error", "Indexing", "Canonical points to a broken or redirecting URL", "canonical टूटे या redirect वाले URL पर",
                         "Google may ignore it. Point the canonical to a working 200 page.",
                         "Google इसे अनदेखा कर सकता है। canonical को चालू (200) पेज पर लगाएँ।"),
    "canonical_multiple": ("warning", "Indexing", "More than one canonical", "एक से ज़्यादा canonical",
                           "Conflicting canonicals get ignored. Keep exactly one.", "आपस में टकराते canonical अनदेखे होते हैं। सिर्फ़ एक रखें।"),
    "noindex": ("notice", "Indexing", "noindex pages", "noindex वाले पेज",
                "These pages won't appear in Google. Fine for private / thin pages — check none are important.",
                "ये पेज Google में नहीं दिखेंगे। प्राइवेट/छोटे पेजों के लिए ठीक; देखें कोई ज़रूरी पेज न हो।"),
    "sitemap_bad_url": ("warning", "Indexing", "Sitemap lists non-indexable URLs", "sitemap में non-indexable URL",
                        "Only list working (200), indexable, canonical pages in the sitemap.",
                        "sitemap में सिर्फ़ चालू (200), indexable और canonical पेज रखें।"),
    "not_in_sitemap": ("notice", "Indexing", "Indexable pages missing from the sitemap", "indexable पेज जो sitemap में नहीं",
                       "Add them to the XML sitemap so Google finds them faster.", "इन्हें XML sitemap में जोड़ें ताकि Google जल्दी ढूँढे।"),
    "no_sitemap": ("warning", "Indexing", "No XML sitemap found", "XML sitemap नहीं मिला",
                   "Create /sitemap.xml and list it in robots.txt (most SEO plugins do this).",
                   "/sitemap.xml बनाएँ और robots.txt में लिखें (ज़्यादातर SEO प्लगइन यह कर देते हैं)।"),
    # ---- images
    "img_alt_missing": ("warning", "Images", "Images without alt text", "बिना alt टेक्स्ट वाली इमेज",
                        "Alt text helps blind users and Google Images. Describe the image in a few words (empty alt only for decoration).",
                        "alt टेक्स्ट नेत्रहीन यूज़र और Google Images के लिए ज़रूरी है। कुछ शब्दों में इमेज बताएँ।"),
    "img_large": ("warning", "Images", "Large images (over 200 KB)", "बड़ी इमेज (200 KB से ज़्यादा)",
                  "Big images slow the page. Compress them and use WebP/AVIF at the size shown.",
                  "बड़ी इमेज पेज धीमा करती हैं। इन्हें कंप्रेस करें और WebP/AVIF इस्तेमाल करें।"),
    "img_broken": ("error", "Images", "Broken images", "टूटी इमेज",
                   "The image file is missing. Re-upload it or fix the path.", "इमेज फ़ाइल नहीं है। दोबारा अपलोड करें या पाथ ठीक करें।"),
    # ---- security & mobile & structured data
    "mixed_content": ("error", "Security", "Mixed content (http files on https pages)", "मिक्स्ड कंटेंट (https पेज पर http फ़ाइलें)",
                      "Browsers block or warn about these. Load scripts, styles and images over https.",
                      "ब्राउज़र इन्हें रोकते हैं या चेतावनी देते हैं। स्क्रिप्ट, स्टाइल और इमेज https से लोड करें।"),
    "no_hsts": ("notice", "Security", "No HSTS header", "HSTS हेडर नहीं",
                "HSTS makes browsers always use https. Add a Strict-Transport-Security header.",
                "HSTS से ब्राउज़र हमेशा https इस्तेमाल करता है। Strict-Transport-Security हेडर जोड़ें।"),
    "viewport_missing": ("warning", "Mobile", "No mobile viewport tag", "मोबाइल viewport टैग नहीं",
                         "Without it the page looks tiny on phones. Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">.",
                         "इसके बिना फ़ोन पर पेज बहुत छोटा दिखता है। viewport meta टैग जोड़ें।"),
    "lang_missing": ("notice", "Mobile", "No language set (<html lang>)", "भाषा नहीं बताई (<html lang>)",
                     "Tell browsers and Google the page language, e.g. <html lang=\"hi\">.",
                     "ब्राउज़र और Google को पेज की भाषा बताएँ, जैसे <html lang=\"hi\">।"),
    "jsonld_invalid": ("error", "Structured data", "Broken structured data (invalid JSON-LD)", "टूटा structured data (गलत JSON-LD)",
                       "Google can't read it, so rich results are lost. Fix the JSON syntax.",
                       "Google इसे नहीं पढ़ पाता, इसलिए rich results नहीं मिलते। JSON सही करें।"),
    "no_structured_data": ("notice", "Structured data", "No structured data", "कोई structured data नहीं",
                           "Schema (Organization, Product, Article, FAQ…) can earn stars and rich results in Google.",
                           "Schema (Organization, Product, Article, FAQ…) से Google में स्टार और rich results मिल सकते हैं।"),
    "og_missing": ("notice", "Social", "No Open Graph tags", "Open Graph टैग नहीं",
                   "Without og:title/og:image, links shared on WhatsApp/Facebook look plain.",
                   "og:title/og:image के बिना WhatsApp/Facebook पर शेयर किए लिंक फीके दिखते हैं।"),
    # ---- URLs
    # ---- links (link score)
    "few_inlinks": ("notice", "Links", "Pages linked from only one page", "सिर्फ़ एक पेज से लिंक वाले पेज",
                    "Pages with a single internal link get little link authority. Link important ones from more relevant pages.",
                    "एक ही अंदरूनी लिंक वाले पेज को कम ताकत मिलती है। ज़रूरी पेजों को और भी मिलते-जुलते पेजों से लिंक करें।"),
    # ---- structured data (Google rich results)
    "sd_required": ("error", "Structured data", "Structured data missing required fields", "structured data में ज़रूरी field नहीं",
                    "Google won't show rich results (stars, prices, FAQs) without these fields. Add the missing properties shown.",
                    "इन field के बिना Google rich results (स्टार, कीमत, FAQ) नहीं दिखाता। दिखाई गई property जोड़ें।"),
    "sd_recommended": ("notice", "Structured data", "Structured data missing recommended fields", "structured data में सुझाए गए field नहीं",
                       "Optional, but adding them makes the result richer and more likely to show.",
                       "ज़रूरी नहीं, पर जोड़ने से रिज़ल्ट बेहतर और ज़्यादा दिखने लायक बनता है।"),
    # ---- accessibility
    "a11y_form_label": ("warning", "Accessibility", "Form fields without a label", "बिना label वाले फ़ॉर्म field",
                        "Screen-reader users can't tell what to type. Add a <label for=...> or aria-label.",
                        "स्क्रीन-रीडर वाले यूज़र नहीं जान पाते क्या लिखना है। <label for=...> या aria-label जोड़ें।"),
    "a11y_link_text": ("warning", "Accessibility", "Links without text", "बिना टेक्स्ट वाले लिंक",
                       "Icon-only links are announced as just 'link'. Add text, aria-label, or alt on the image.",
                       "सिर्फ़ आइकन वाले लिंक को स्क्रीन-रीडर बस 'link' बोलता है। टेक्स्ट, aria-label या इमेज पर alt जोड़ें।"),
    "a11y_button_name": ("warning", "Accessibility", "Buttons without a name", "बिना नाम वाले बटन",
                         "Give each button visible text or an aria-label.", "हर बटन को दिखने वाला टेक्स्ट या aria-label दें।"),
    "a11y_empty_heading": ("notice", "Accessibility", "Empty headings", "खाली हेडिंग",
                           "Headings without text confuse screen readers. Remove them or add text.",
                           "बिना टेक्स्ट की हेडिंग स्क्रीन-रीडर को उलझाती है। हटाएँ या टेक्स्ट जोड़ें।"),
    "a11y_heading_skip": ("notice", "Accessibility", "Heading levels skipped (e.g. H2 → H4)", "हेडिंग लेवल छूटे (जैसे H2 → H4)",
                          "Keep headings in order so the page outline makes sense.", "हेडिंग क्रम से रखें ताकि पेज की रूपरेखा समझ आए।"),
    "axe_serious": ("error", "Accessibility", "Serious accessibility problems (WCAG, axe)", "गंभीर accessibility गड़बड़ियाँ (WCAG, axe)",
                    "These block people using screen readers or keyboards, and can be a legal risk. Each line links the rule to fix.",
                    "ये स्क्रीन-रीडर या कीबोर्ड वाले लोगों को रोकती हैं और कानूनी जोखिम भी हो सकता है। हर लाइन में ठीक करने का नियम है।"),
    "axe_minor": ("notice", "Accessibility", "Minor accessibility problems (WCAG, axe)", "छोटी accessibility गड़बड़ियाँ (WCAG, axe)",
                  "Smaller barriers worth fixing when you can.", "छोटी रुकावटें, मौका मिलने पर ठीक करें।"),
    # ---- custom search
    "custom_found": ("notice", "Custom search", "Custom search: text found", "कस्टम सर्च: टेक्स्ट मिला",
                     "Pages containing the text you searched for.", "वे पेज जिनमें आपका खोजा टेक्स्ट है।"),
    "custom_missing": ("warning", "Custom search", "Custom search: text missing", "कस्टम सर्च: टेक्स्ट नहीं मिला",
                       "Pages that don't contain the text you expected (e.g. an analytics code).",
                       "वे पेज जिनमें अपेक्षित टेक्स्ट नहीं (जैसे analytics कोड)।"),
    # ---- page speed (PageSpeed Insights)
    "cwv_poor": ("error", "Page speed", "Poor Core Web Vitals", "ख़राब Core Web Vitals",
                 "Google uses these in ranking. LCP over 4 s or CLS over 0.25 (or INP over 500 ms) is poor: compress images, cut render-blocking scripts, reserve space for ads/images.",
                 "Google रैंकिंग में इन्हें देखता है। LCP 4 सेकंड से ज़्यादा या CLS 0.25 से ज़्यादा (या INP 500 ms से ज़्यादा) ख़राब है: इमेज कंप्रेस करें, भारी स्क्रिप्ट कम करें, इमेज/विज्ञापन के लिए जगह पहले से रखें।"),
    "cwv_improve": ("warning", "Page speed", "Core Web Vitals need improvement", "Core Web Vitals में सुधार चाहिए",
                    "LCP over 2.5 s, CLS over 0.1 or INP over 200 ms. Close to good - small fixes help.",
                    "LCP 2.5 सेकंड से ज़्यादा, CLS 0.1 से ज़्यादा या INP 200 ms से ज़्यादा। अच्छे के करीब - छोटे सुधार काफ़ी हैं।"),
    "speed_low": ("warning", "Page speed", "Low PageSpeed score (under 50)", "कम PageSpeed स्कोर (50 से कम)",
                  "Lighthouse found big speed problems; open the page in PageSpeed Insights for the full list.",
                  "Lighthouse को बड़ी स्पीड गड़बड़ियाँ मिलीं; पूरी सूची के लिए पेज PageSpeed Insights में खोलें।"),
    # ---- Search Console
    "gsc_traffic_problem": ("error", "Search Console", "Pages with Google traffic that have problems", "Google ट्रैफ़िक वाले पेज जिनमें गड़बड़ी है",
                            "These pages get clicks from Google but are broken, redirecting or noindex now - you are losing that traffic. Fix them first.",
                            "इन पेजों पर Google से क्लिक आते हैं पर अब ये टूटे, redirect या noindex हैं - ट्रैफ़िक जा रहा है। इन्हें सबसे पहले ठीक करें।"),
    "gsc_not_linked": ("warning", "Search Console", "Pages Google shows that the crawl didn't reach", "Google में दिखने वाले पेज जिन तक क्रॉल नहीं पहुँचा",
                       "Google knows these pages but no internal link leads there. Link them from your site.",
                       "Google इन पेजों को जानता है पर साइट का कोई लिंक यहाँ नहीं आता। साइट से लिंक करें।"),
    "gsc_low_ctr": ("notice", "Search Console", "High impressions, low click rate", "ज़्यादा impressions, कम क्लिक",
                    "Shown often on page 1 but rarely clicked. Rewrite the title and description to be more compelling.",
                    "पहले पेज पर अक्सर दिखता है पर क्लिक कम। टाइटल और description ज़्यादा आकर्षक लिखें।"),
    # ---- server logs
    "log_bot_errors": ("warning", "Logs", "Search bots hitting error pages", "सर्च बॉट एरर पेजों पर आ रहे हैं",
                       "Bots waste their visits on 4xx/5xx URLs. Fix or redirect these and remove links to them.",
                       "बॉट 4xx/5xx URL पर अपनी विज़िट बर्बाद करते हैं। इन्हें ठीक या redirect करें और लिंक हटाएँ।"),
    "log_not_seen": ("notice", "Logs", "Pages Googlebot didn't visit (in these logs)", "पेज जिन पर Googlebot नहीं आया (इन लॉग में)",
                     "Google may not consider them important. Link to them more and add them to the sitemap.",
                     "Google इन्हें शायद ज़रूरी नहीं मानता। इन पर ज़्यादा लिंक दें और sitemap में जोड़ें।"),
    "log_param_waste": ("notice", "Logs", "Bots crawling ?parameter URLs", "बॉट ?parameter वाले URL क्रॉल कर रहे हैं",
                        "Crawl budget goes to filter/sort URLs. Use canonicals, or block useless parameters in robots.txt.",
                        "क्रॉल बजट filter/sort वाले URL पर जा रहा है। canonical लगाएँ या बेकार parameter robots.txt में ब्लॉक करें।"),
    "url_uppercase": ("notice", "URLs", "URLs with capital letters", "बड़े अक्षर वाले URL",
                      "URLs are case-sensitive; mixed case causes duplicates. Use lower case.",
                      "URL में बड़े-छोटे अक्षर अलग माने जाते हैं, इससे डुप्लिकेट बनते हैं। छोटे अक्षर रखें।"),
    "url_underscore": ("notice", "URLs", "URLs with underscores", "underscore (_) वाले URL",
                       "Google treats hyphens as word separators, not underscores. Prefer my-page over my_page.",
                       "Google hyphen (-) को शब्दों का अंतर मानता है, underscore को नहीं। my-page बेहतर है।"),
    "url_long": ("notice", "URLs", "Long URLs (over 115 characters)", "लंबे URL (115 अक्षर से ज़्यादा)",
                 "Short, readable URLs are easier to share and understand.", "छोटे, पढ़ने लायक URL शेयर करना और समझना आसान है।"),
    "url_params": ("notice", "URLs", "URLs with ?parameters", "?parameter वाले URL",
                   "Parameters can create many duplicate URLs. Use canonicals or clean URLs.",
                   "parameter से कई डुप्लिकेट URL बन सकते हैं। canonical या साफ़ URL इस्तेमाल करें।"),
    # ---- AI search
    "ai_bots_blocked": ("warning", "AI search", "AI assistants are blocked in robots.txt", "robots.txt में AI असिस्टेंट ब्लॉक हैं",
                        "ChatGPT, Claude, Perplexity or Google's AI can't read the site, so it won't be cited in AI answers. Allow them unless that's your choice.",
                        "ChatGPT, Claude, Perplexity या Google AI साइट नहीं पढ़ पाते, तो AI जवाबों में आपकी साइट नहीं आएगी। जानबूझकर नहीं है तो इन्हें allow करें।"),
    "llms_txt_missing": ("notice", "AI search", "No llms.txt", "llms.txt नहीं है",
                         "An /llms.txt file is a new, optional summary of your site for AI assistants.",
                         "/llms.txt एक नई, वैकल्पिक फ़ाइल है जो AI असिस्टेंट को आपकी साइट का सार बताती है।"),
}

SEVERITY_ORDER = {"error": 0, "warning": 1, "notice": 2}

HTML_PAGES = ("internal = 1 AND resource = 0 AND status = 200 AND "
              "content_type IN ('text/html', 'application/xhtml+xml')")


def analyse(db):
    db.execute("DELETE FROM issues")
    rows = []

    def add(code, url, detail=""):
        rows.append((code, url, str(detail)[:500]))

    pages = db.query("SELECT * FROM pages")
    by_url = {p["url"]: p for p in pages}
    html = [p for p in pages if p["internal"] and not p["resource"] and p["status"] == 200
            and p["content_type"] in ("text/html", "application/xhtml+xml")]
    html_urls = {p["url"] for p in html}
    start = db.query("SELECT url FROM pages WHERE source = 'start'")
    https_site = bool(start) and start[0]["url"].startswith("https://")

    # inlinks (from crawled pages, <a> only)
    inlinks = defaultdict(list)
    for link in db.query("SELECT src, dst, anchor, nofollow, kind FROM links"):
        inlinks[link["dst"]].append(link)

    # ---- responses
    for p in pages:
        internal_page = p["internal"] and not p["resource"]
        if p["blocked"]:
            add("blocked_robots", p["url"])
        if p["error"] and internal_page:
            add("no_response", p["url"], p["error"])
        if not internal_page or p["status"] is None:
            continue
        if 400 <= p["status"] < 500:
            add("client_error", p["url"], f"{p['status']} - linked from {len(inlinks[p['url']])} place(s)")
        elif p["status"] >= 500:
            add("server_error", p["url"], p["status"])
        if p["status"] == 200 and (p["time_ms"] or 0) > 1500 and p["url"] in html_urls:
            add("slow_page", p["url"], f"{p['time_ms'] / 1000:.1f} s")
        if https_site and p["url"].startswith("http://"):
            add("http_url", p["url"])

    # ---- redirects
    for p in pages:
        if not p["redirect_to"] or not p["internal"]:
            continue
        chain, cur, loop = [p["url"]], p["redirect_to"], False
        while cur and len(chain) < 10:
            if cur in chain:
                loop = True
                break
            chain.append(cur)
            nxt = by_url.get(cur)
            cur = nxt["redirect_to"] if nxt else None
        if loop:
            add("redirect_loop", p["url"], " → ".join(chain + [cur]))
        elif len(chain) > 2:
            add("redirect_chain", p["url"], " → ".join(chain))
        for link in inlinks[p["url"]]:
            if link["kind"] == "a":
                add("link_to_redirect", link["src"], f"{p['url']} → {p['redirect_to']}")

    # ---- links
    for dst, links in inlinks.items():
        target = by_url.get(dst)
        if not target:
            continue
        bad = (target["status"] or 0) >= 400 or (target["error"] and not target["blocked"])
        what = target["status"] or target["error"] or ""
        for link in links:
            if link["kind"] == "a" and bad:
                code = "broken_internal_link" if target["internal"] else "broken_external_link"
                add(code, link["src"], f"{dst} ({what})" + (f" - '{link['anchor']}'" if link["anchor"] else ""))
            elif link["kind"] == "img" and bad:
                add("img_broken", link["src"], f"{dst} ({what})")
            if link["kind"] == "a" and link["nofollow"] and target["internal"]:
                add("nofollow_internal", link["src"], dst)
    outlinks = defaultdict(int)
    alts = []
    for link in db.query("SELECT src, dst, anchor, kind FROM links WHERE kind IN ('a', 'img')"):
        if link["kind"] == "a" and by_url.get(link["dst"], {}).get("internal"):
            outlinks[link["src"]] += 1
        elif link["kind"] == "img":
            alts.append(link)
    for link in alts:
        if link["anchor"] is None:
            add("img_alt_missing", link["src"], link["dst"])
    seen_img = set()
    for link in alts:
        img = by_url.get(link["dst"])
        if img and img["size"] and img["size"] > 200 * 1024 and link["dst"] not in seen_img:
            seen_img.add(link["dst"])
            add("img_large", link["dst"], f"{img['size'] // 1024} KB (on {link['src']})")

    sitemap = {r["url"] for r in db.query("SELECT url FROM sitemap")}
    for p in html:
        if p["render_error"]:
            add("render_failed", p["url"], p["render_error"])
        elif p["rendered"]:
            words, raw_words = p["words"] or 0, p["raw_words"] or 0
            links, raw_links = outlinks[p["url"]], p["raw_links"] or 0
            if (words >= 50 and words > raw_words * 1.5) or links > raw_links + 5:
                add("js_content", p["url"], f"words {raw_words} → {words}, internal links "
                    f"{raw_links} → {links} (raw HTML → rendered)")
        if not outlinks[p["url"]]:
            add("no_outlinks", p["url"])
        if p["source"] == "sitemap":
            add("orphan_page", p["url"])
        if p["depth"] is not None and p["depth"] > 3:
            add("deep_page", p["url"], f"{p['depth']} clicks")

    # ---- titles, descriptions, headings
    titles, descs, h1s = defaultdict(list), defaultdict(list), defaultdict(list)
    for p in html:
        t = (p["title"] or "").strip()
        if not t:
            add("title_missing", p["url"])
        else:
            titles[t.lower()].append(p["url"])
            if len(t) > 60:
                add("title_long", p["url"], f"{len(t)} chars: {t}")
            elif len(t) < 30:
                add("title_short", p["url"], f"{len(t)} chars: {t}")
        if (p["titles"] or 0) > 1:
            add("title_multiple", p["url"], f"{p['titles']} titles")
        d = (p["meta_desc"] or "").strip()
        if not d:
            add("desc_missing", p["url"])
        else:
            descs[d.lower()].append(p["url"])
            if len(d) > 160:
                add("desc_long", p["url"], f"{len(d)} chars")
            elif len(d) < 70:
                add("desc_short", p["url"], f"{len(d)} chars: {d}")
        if (p["meta_descs"] or 0) > 1:
            add("desc_multiple", p["url"], f"{p['meta_descs']} descriptions")
        heads = json.loads(p["h1"] or "[]")
        if not heads:
            add("h1_missing", p["url"])
        else:
            h1s[heads[0].strip().lower()].append(p["url"])
            if len(heads) > 1:
                add("h1_multiple", p["url"], " | ".join(heads)[:300])
        if not p["h2s"]:
            add("h2_missing", p["url"])
    for group, code in ((titles, "title_duplicate"), (descs, "desc_duplicate"), (h1s, "h1_duplicate")):
        for text, urls in group.items():
            if len(urls) > 1 and text:
                for u in urls:
                    add(code, u, f"{len(urls)} pages share: {text[:120]}")

    # ---- content
    hashes = defaultdict(list)
    for p in html:
        if (p["words"] or 0) < 200:
            add("thin_content", p["url"], f"{p['words']} words")
        if p["text_hash"]:
            hashes[p["text_hash"]].append(p["url"])
    exact = set()
    for urls in hashes.values():
        if len(urls) > 1:
            for u in urls:
                exact.add(u)
                add("duplicate_content", u, f"same text as {len(urls) - 1} other page(s), e.g. "
                    f"{next(x for x in urls if x != u)}")
    for a, b in near_duplicates([p for p in html if p["url"] not in exact and (p["words"] or 0) >= 50]):
        add("near_duplicate", a, f"very similar to {b}")
        add("near_duplicate", b, f"very similar to {a}")

    # ---- indexing
    indexable = []
    for p in html:
        directives = f"{p['meta_robots'] or ''} {p['x_robots'] or ''}".lower()
        canon = json.loads(p["canonical"] or "[]")
        noindex = "noindex" in directives or "none" in directives.split(", ")
        if noindex:
            add("noindex", p["url"], directives.strip())
        if not canon:
            add("canonical_missing", p["url"])
        if len(set(canon)) > 1:
            add("canonical_multiple", p["url"], " | ".join(canon))
        target = canon[0] if canon else p["url"]
        target = normalize(target) or target
        if target != p["url"]:
            add("canonicalised", p["url"], target)
            t = by_url.get(target)
            if t and (t["status"] != 200):
                add("canonical_broken", p["url"], f"{target} ({t['status'] or t['error']})")
        if not noindex and target == p["url"]:
            indexable.append(p["url"])
        if not p["viewport"]:
            add("viewport_missing", p["url"])
        if not p["lang"]:
            add("lang_missing", p["url"])
        if p["jsonld_bad"]:
            add("jsonld_invalid", p["url"], f"{p['jsonld_bad']} invalid block(s)")
        if not p["jsonld"] and not p["jsonld_bad"]:
            add("no_structured_data", p["url"])
        if not p["og"]:
            add("og_missing", p["url"])
        if p["mixed"]:
            add("mixed_content", p["url"], f"{p['mixed']} http file(s)")
        path = urlsplit(p["url"]).path
        if path != path.lower():
            add("url_uppercase", p["url"])
        if "_" in path:
            add("url_underscore", p["url"])
        if len(p["url"]) > 115:
            add("url_long", p["url"], f"{len(p['url'])} chars")
        if urlsplit(p["url"]).query:
            add("url_params", p["url"])
    if sitemap:
        idx = set(indexable)
        for u in sitemap:
            p = by_url.get(u)
            if p and p["internal"] and u not in idx:
                add("sitemap_bad_url", u, p["status"] or p["error"] or "not indexable")
        for u in indexable:
            if u not in sitemap:
                add("not_in_sitemap", u)
    elif start:
        add("no_sitemap", start[0]["url"])

    if start:
        s = by_url.get(start[0]["url"]) or {}
        if https_site and s.get("status") == 200 and not s.get("hsts"):
            add("no_hsts", start[0]["url"])
        root = "{0.scheme}://{0.netloc}".format(urlsplit(start[0]["url"]))
        if db.meta("render_error"):
            add("render_unavailable", start[0]["url"], db.meta("render_error"))
        if db.meta("robots_error"):
            add("robots_unreachable", root + "/robots.txt", db.meta("robots_error"))
        blocked = json.loads(db.meta("ai_bots_blocked", "[]"))
        if blocked:
            add("ai_bots_blocked", root + "/robots.txt", ", ".join(blocked))
        if not json.loads(db.meta("llms_txt", "false")):
            add("llms_txt_missing", root + "/llms.txt")

    link_scores(db, html, by_url)
    structured_data_checks(db, add)
    accessibility_checks(db, html, add)
    for r in db.query("SELECT url, name, value FROM custom"):
        add("custom_missing" if r["value"] == "missing" else "custom_found", r["url"],
            f"{r['name']}: {r['value']}")
    for r in db.query("SELECT url, src_count FROM (SELECT l.dst AS url, COUNT(DISTINCT l.src) "
                      "AS src_count FROM links l WHERE l.kind = 'a' GROUP BY l.dst)"):
        p = by_url.get(r["url"])
        if p and p["url"] in html_urls and p["source"] != "start" and r["src_count"] == 1:
            add("few_inlinks", p["url"])
    speed_checks(db, add)
    search_console_checks(db, by_url, html, indexable, add)
    log_checks(db, html, indexable, add)

    db.executemany("INSERT INTO issues VALUES (?, ?, ?)", rows)
    db.commit()
    return len(rows)


def link_scores(db, html, by_url, damping=0.85, rounds=40):
    """Internal PageRank over <a> links between HTML pages, shown as 0-100 (log scale, like
    Screaming Frog's Link Score). One hop of redirect is followed."""
    pages = [p["url"] for p in html]
    if not pages:
        return
    index = {u: i for i, u in enumerate(pages)}
    out = defaultdict(set)
    for link in db.query("SELECT src, dst FROM links WHERE kind = 'a' AND nofollow = 0"):
        dst = link["dst"]
        target = by_url.get(dst)
        if target and target["redirect_to"]:
            dst = target["redirect_to"]
        if link["src"] in index and dst in index and dst != link["src"]:
            out[index[link["src"]]].add(index[dst])
    n = len(pages)
    rank = [1 / n] * n
    for _ in range(rounds):
        nxt = [(1 - damping) / n] * n
        dangling = sum(rank[i] for i in range(n) if not out[i])
        for i in range(n):
            if out[i]:
                share = damping * rank[i] / len(out[i])
                for j in out[i]:
                    nxt[j] += share
        spread = damping * dangling / n
        rank = [r + spread for r in nxt]
    import math
    lo, hi = math.log(min(rank)), math.log(max(rank))
    scores = [100 if hi == lo else round(100 * (math.log(r) - lo) / (hi - lo)) for r in rank]
    db.executemany("UPDATE pages SET link_score = ? WHERE url = ?",
                   [(sc, u) for u, sc in zip(pages, scores)])


# Google rich result types: required (each tuple = one of these) and recommended properties.
SD_REQUIRED = {
    "Product": [("name",), ("offers", "review", "aggregateRating")],
    "Offer": [("price", "priceSpecification"), ("priceCurrency", "priceSpecification")],
    "AggregateRating": [("ratingValue",), ("ratingCount", "reviewCount")],
    "Review": [("author",), ("reviewRating",)],
    "BreadcrumbList": [("itemListElement",)],
    "ListItem": [("position",)],
    "FAQPage": [("mainEntity",)],
    "Question": [("name",), ("acceptedAnswer", "suggestedAnswer")],
    "Answer": [("text",)],
    "Event": [("name",), ("startDate",), ("location",)],
    "Recipe": [("name",), ("image",)],
    "VideoObject": [("name",), ("thumbnailUrl",), ("uploadDate",)],
    "JobPosting": [("title",), ("description",), ("datePosted",), ("hiringOrganization",),
                   ("jobLocation", "applicantLocationRequirements")],
    "LocalBusiness": [("name",), ("address",)],
    "SoftwareApplication": [("name",), ("offers",), ("aggregateRating", "review")],
    "Course": [("name",), ("description",), ("provider",)],
}
SD_RECOMMENDED = {
    "Article": ["headline", "image", "datePublished", "author"],
    "NewsArticle": ["headline", "image", "datePublished", "author"],
    "BlogPosting": ["headline", "image", "datePublished", "author"],
    "Organization": ["name", "url", "logo"],
    "Product": ["image", "description", "brand"],
    "LocalBusiness": ["telephone", "openingHoursSpecification", "geo"],
    "Event": ["image", "description", "endDate", "offers"],
}
LOCAL_BUSINESS = {"LocalBusiness", "Restaurant", "Store", "Dentist", "Hotel", "MedicalClinic",
                  "AutoRepair", "BeautySalon", "LegalService", "RealEstateAgent", "Physician",
                  "HealthAndBeautyBusiness", "HomeAndConstructionBusiness", "FoodEstablishment",
                  "ProfessionalService", "Electrician", "Plumber", "Locksmith", "CafeOrCoffeeShop"}


def structured_data_checks(db, add):
    for r in db.query("SELECT url, type, json FROM structured"):
        node = json.loads(r["json"])
        kind = "LocalBusiness" if r["type"] in LOCAL_BUSINESS else r["type"]
        missing = [" or ".join(alts) for alts in SD_REQUIRED.get(kind, [])
                   if not any(node.get(a) not in (None, "", []) for a in alts)]
        if missing:
            add("sd_required", r["url"], f"{r['type']}: missing {', '.join(missing)}")
        rec = [a for a in SD_RECOMMENDED.get(kind, []) if node.get(a) in (None, "", [])]
        if rec:
            add("sd_recommended", r["url"], f"{r['type']}: add {', '.join(rec)}")


def accessibility_checks(db, html, add):
    codes = {"form_field_no_label": "a11y_form_label", "link_no_text": "a11y_link_text",
             "button_no_name": "a11y_button_name", "empty_heading": "a11y_empty_heading",
             "heading_skipped": "a11y_heading_skip"}
    for p in html:
        for key, n in json.loads(p["a11y"] or "{}").items():
            if key in codes:
                add(codes[key], p["url"], f"{n} on this page")
    for r in db.query("SELECT url, rule, impact, help, count, help_url FROM a11y"):
        code = "axe_serious" if r["impact"] in ("critical", "serious") else "axe_minor"
        add(code, r["url"], f"{r['impact']}: {r['help']} ({r['count']}x) - {r['help_url']}")


def speed_checks(db, add):
    for r in db.query("SELECT * FROM cwv WHERE error IS NULL"):
        field = json.loads(r["field"] or "{}")
        lcp = field.get("lcp") or r["lcp"]
        cls = field.get("cls") if field.get("cls") is not None else r["cls"]
        inp = field.get("inp")
        detail = (f"{r['strategy']}: LCP {lcp / 1000:.1f} s, CLS {cls:.2f}"
                  + (f", INP {inp:.0f} ms" if inp else "") + f", score {r['score']}"
                  + (" (real users)" if field else " (lab test)"))
        if (lcp or 0) > 4000 or (cls or 0) > 0.25 or (inp or 0) > 500:
            add("cwv_poor", r["url"], detail)
        elif (lcp or 0) > 2500 or (cls or 0) > 0.1 or (inp or 0) > 200:
            add("cwv_improve", r["url"], detail)
        if r["score"] is not None and r["score"] < 50:
            add("speed_low", r["url"], detail)


def search_console_checks(db, by_url, html, indexable, add):
    rows = db.query("SELECT * FROM gsc")
    if not rows:
        return
    idx = set(indexable)
    for g in rows:
        p = by_url.get(g["url"])
        if p is None:
            if (g["impressions"] or 0) > 0:
                add("gsc_not_linked", g["url"], f"{g['clicks']} clicks, {g['impressions']} impressions")
            continue
        if (g["clicks"] or 0) > 0 and (p["status"] != 200 or g["url"] not in idx):
            why = (p["status"] if p["status"] != 200 else "noindex / canonicalised") or p["error"]
            add("gsc_traffic_problem", g["url"], f"{g['clicks']} clicks - now {why}")
        if (g["impressions"] or 0) >= 100 and (g["ctr"] or 0) < 0.01 and (g["position"] or 99) <= 10:
            add("gsc_low_ctr", g["url"], f"{g['impressions']} impressions, CTR {g['ctr'] * 100:.1f}%, "
                f"position {g['position']:.1f}")


def log_checks(db, html, indexable, add):
    rows = db.query("SELECT url, bot, hits, statuses FROM logs")
    if not rows:
        return
    google_seen = set()
    for r in rows:
        statuses = json.loads(r["statuses"] or "{}")
        bad = sum(n for code, n in statuses.items() if code[0] in "45")
        if bad:
            add("log_bot_errors", r["url"], f"{r['bot']}: {bad} of {r['hits']} hits got 4xx/5xx")
        if urlsplit(r["url"]).query:
            add("log_param_waste", r["url"], f"{r['bot']}: {r['hits']} hits")
        if r["bot"] == "Googlebot":
            google_seen.add(r["url"])
    if google_seen:
        for u in indexable:
            if u not in google_seen:
                add("log_not_seen", u)


def near_duplicates(pages, max_bits=3):
    """Pairs of pages whose SimHash differs in at most `max_bits` bits.

    Split the 64 bits into 4 bands of 16: two hashes within 3 bits must share a
    band exactly, so only pages sharing a band are compared (fast on big sites).
    """
    buckets = defaultdict(list)
    hashes = {}
    for p in pages:
        h = p["simhash"] or 0
        if not h:
            continue
        h &= (1 << 64) - 1
        hashes[p["url"]] = h
        for band in range(4):
            buckets[(band, h >> (band * 16) & 0xFFFF)].append(p["url"])
    pairs = set()
    for urls in buckets.values():
        if len(urls) > 200:  # a template-only band; skip to stay fast
            continue
        for i, a in enumerate(urls):
            for b in urls[i + 1:]:
                if (a, b) not in pairs and bin(hashes[a] ^ hashes[b]).count("1") <= max_bits:
                    pairs.add((a, b))
    return sorted(pairs)


def health_score(db):
    """Percent of HTML pages with no error-level issue (None if there are no pages)."""
    errors = ",".join(f"'{k}'" for k, v in CHECKS.items() if v[0] == "error")
    total = db.query(f"SELECT COUNT(*) AS n FROM pages WHERE {HTML_PAGES}")[0]["n"]
    bad = db.query(f"SELECT COUNT(DISTINCT url) AS n FROM issues WHERE code IN ({errors}) "
                   f"AND url IN (SELECT url FROM pages WHERE {HTML_PAGES})")[0]["n"]
    return round(100 * (total - bad) / total) if total else None


def summary(db):
    """Issue counts per code, with descriptions, most severe first."""
    counts = {r["code"]: r["n"] for r in db.query(
        "SELECT code, COUNT(DISTINCT url) AS n FROM issues GROUP BY code")}
    out = []
    for code, n in counts.items():
        sev, cat, title, title_hi, fix, fix_hi = CHECKS[code]
        out.append({"code": code, "severity": sev, "category": cat, "title": title,
                    "title_hi": title_hi, "fix": fix, "fix_hi": fix_hi, "count": n})
    out.sort(key=lambda r: (SEVERITY_ORDER[r["severity"]], -r["count"]))
    return out
