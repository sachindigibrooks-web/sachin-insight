B = "https://harlingenglass.com"
# id, batch, date, category, gbp_type, topic, keyword, offer_title, copy, cta, landing, utm_content, offer_terms, image, notes
POSTS = [
("HG-01", 1, "2026-11-03", "Service", "Update", "Residential window glass repair", "window glass repair Harlingen", "",
"""Cracked pane, a window hit by a stray ball, or glass that looks foggy between the panes? Harlingen Glass & Mirror repairs and replaces residential glass across Harlingen and the Rio Grande Valley.

We work on single and double-pane windows, sliding and swinging glass doors, tabletops and shelves. If it is made of glass, our team can fix it, replace it or install it.

Family-owned since 1978, we measure on site and give you a clear quote before any work starts. Tap Learn more to request your free estimate.""",
"Learn more", B+"/service/residential/", "hg01-window-repair", "",
"Real photo: technician replacing a residential window pane (before/after if available).", ""),

("HG-02", 1, "2026-11-05", "Promotional", "Offer", "Window replacement offer", "window replacement Harlingen", "Buy 3 Windows, Get the 4th Window Free",
"""Old or drafty windows can push your energy bills up and leave hot and cold spots around the house. This season, upgrade to energy-efficient windows with Harlingen Glass & Mirror.

Buy 3 windows and get the 4th window free. Every project starts with a free window inspection, expert advice and a clear quote, with no pressure.

Serving Harlingen and the Rio Grande Valley for over 40 years. Tap View offer to book your free inspection.""",
"View offer", B+"/service/residential-window-replacement/", "hg02-buy3-get1",
"Offer dates: Nov 5 to Nov 30, 2026 (confirm). Terms: confirm eligible window types, minimum order and whether it combines with financing.",
"Real photo: newly installed residential windows, exterior view.", "Offer is live on the website. Confirm dates and terms with the client before publishing."),

("HG-03", 2, "2026-11-10", "FAQ", "Update", "Foggy double-pane windows", "foggy window repair", "",
"""FAQ: Why is my double-pane window foggy, and can it be fixed?

Fog or moisture trapped between the two panes usually means the seal on the insulated glass unit has failed. Once that happens, the window loses much of its insulating value and cleaning will not clear it.

In many cases the glass unit can be replaced without replacing the whole window frame. Our team will look at the window, explain your options and give you a clear quote.

Tap Learn more to book a free assessment with Harlingen Glass & Mirror.""",
"Learn more", B+"/service/residential/", "hg03-faq-foggy-glass", "",
"Close-up photo of a fogged double-pane window next to a clear replacement.", "Confirm the team replaces sealed units (IGUs) only, not just full windows."),

("HG-04", 2, "2026-11-12", "Local", "Update", "Family-owned since 1978", "glass company Harlingen TX", "",
"""Harlingen Glass & Mirror has been part of the Harlingen community since 1978. Today the Shull family leads our team, and we still treat every customer like family.

From homeowners and realtors to contractors and local businesses, the Valley has trusted us for more than 45 years with glass repair, shower enclosures, mirrors, windows and commercial glazing.

Visit us at 1905 E. Harrison Ave. in Harlingen, Monday to Friday. Tap Learn more to meet the team.""",
"Learn more", B+"/company/", "hg04-local-since-1978", "",
"Team photo in front of the shop or the Shull family on site.", "Address in post text is allowed. Do not add the phone number."),

("HG-05", 3, "2026-11-17", "Service", "Update", "Custom frameless shower enclosures", "frameless shower doors Harlingen", "",
"""Ready to replace that old shower curtain? A custom glass enclosure opens up your bathroom, is easy to keep clean and adds value to your home.

Harlingen Glass & Mirror designs and installs frameless, semi-frameless and framed shower enclosures, sliding doors and glass partitions, made to fit your space.

Book a free bathroom consultation. We will measure, show you the options and give you a clear quote. Financing is available.""",
"Book", B+"/service/bathroom-enclosures/", "hg05-shower-enclosures", "",
"Real before/after photo of a frameless shower enclosure installed by the team.", ""),

("HG-06", 3, "2026-11-19", "FAQ", "Update", "Frameless vs semi-frameless vs framed", "shower enclosure types", "",
"""FAQ: Frameless, semi-frameless or framed: which shower enclosure is right for me?

Framed enclosures use metal around the glass and are usually the most budget-friendly. Semi-frameless enclosures use less metal for a cleaner look. Frameless enclosures use thicker glass with minimal hardware for the most open, modern feel.

Sliding and hinged doors are available, with clear, frosted or patterned glass depending on the privacy you want.

Tap Learn more and our team will help you choose the best fit for your bathroom.""",
"Learn more", B+"/service/bathroom-enclosures/", "hg06-faq-shower-types", "",
"Side-by-side photos of a framed, a semi-frameless and a frameless enclosure.", ""),

("HG-07", 4, "2026-11-24", "Promotional", "Update", "Financing with Synchrony", "glass financing Harlingen", "",
"""Planning a new shower enclosure, window upgrade or mirror project but want to spread the cost?

Harlingen Glass & Mirror has partnered with Synchrony Bank to offer financing options for home remodeling and upgrade projects. Ask about financing when you request your quote.

Our team will measure, recommend the right glass for your project and give you a clear price before any work begins. Tap Learn more to get started.""",
"Learn more", B+"/contact/", "hg07-financing", "",
"Clean photo of a finished bathroom or window project with a simple text-free layout.", "Do not state rates or terms. Confirm the financing partnership is still active."),

("HG-08", 4, "2026-11-25", "Local", "Update", "Thanksgiving thank you", "Harlingen glass company", "",
"""Happy Thanksgiving from all of us at Harlingen Glass & Mirror.

Thank you to the homeowners, realtors, contractors and businesses across Harlingen and the Rio Grande Valley who have trusted our family-owned shop for more than 45 years. Every project you send our way means a lot to our team.

Hosting family this week? If a cracked mirror or a sticky glass door needs attention after the holiday, we are here to help. Tap Learn more to reach our team.""",
"Learn more", B+"/contact/", "hg08-thanksgiving", "",
"Team photo or a warm photo of the shop. No stock images.", "Confirm holiday office hours and update GBP special hours."),

("HG-09", 5, "2026-12-01", "Service", "Update", "3M Security Window Film for schools", "3M security film Texas schools", "",
"""Is your campus ready for Texas Education Agency safety requirements?

Harlingen Glass & Mirror installs 3M Security Window Film to strengthen school windows and glass doors. The film helps hold broken glass together and slows forced entry, giving staff valuable response time.

Work with a 3M authorized team so your film is installed correctly and meets requirements. Tap Book to schedule a free campus walkthrough.""",
"Book", B+"/service/3m-security-film/", "hg09-3m-security-film", "",
"Real photo of security film being installed on school or commercial glass.", "Confirm 3M authorization wording with the client."),

("HG-10", 5, "2026-12-03", "FAQ", "Update", "Is all security film compliant?", "TEA compliant window film", "",
"""FAQ: Does any security window film meet school safety requirements?

Not always. Schools sometimes discover their film does not meet requirements after it has been installed, which can mean paying twice. The film product, how it is attached and who installs it all matter.

Harlingen Glass & Mirror installs 3M Security Window Film as a 3M authorized team and can walk your campus to check vulnerable entry points.

Tap Learn more to request your free security film assessment.""",
"Learn more", B+"/service/3m-security-film/", "hg10-faq-security-film", "",
"Photo of a school entrance with glass doors (own photo or client project).", "Fact-check with the client before publishing."),

("HG-11", 6, "2026-12-08", "Service", "Update", "Commercial storefront glass", "storefront glass repair Harlingen", "",
"""A broken storefront window or door is a security risk and the first thing customers notice.

Harlingen Glass & Mirror repairs and replaces commercial glass for businesses across the Rio Grande Valley, including storefront glass, entry doors, fire-rated glass, thermal glazing and multi-story projects.

With more than 45 years in commercial glazing, our team works to meet safety standards while keeping your property looking professional. Tap Learn more to request a free assessment.""",
"Learn more", B+"/service/commercial-glass/", "hg11-commercial-storefront", "",
"Real photo of a completed storefront installation.", ""),

("HG-12", 6, "2026-12-10", "Promotional", "Offer", "Free security film assessment over winter break", "school window film installation", "Free Security Film Assessment for Schools",
"""Winter break is one of the best times to upgrade campus glass with less disruption for students and staff.

Book a free security film assessment with Harlingen Glass & Mirror. We will walk your campus, check windows and glass doors, and recommend the right 3M Security Window Film for each entry point.

Spots for break installations are limited. Tap View offer to schedule your walkthrough.""",
"View offer", B+"/service/3m-security-film/", "hg12-winter-break-assessment",
"Offer dates: Dec 10, 2026 to Jan 8, 2027 (confirm). Terms: assessment is free, installation quoted separately.",
"Photo of security film install on classroom or office windows.", "Confirm the team has installer availability during winter break."),

("HG-13", 7, "2026-12-15", "Service", "Update", "Custom mirrors", "custom mirrors Harlingen", "",
"""A custom mirror can make a bathroom feel bigger, brighten a bedroom or finish off an entryway.

Harlingen Glass & Mirror cuts and installs custom mirrors for homes and businesses across the Rio Grande Valley. We help you choose the size, edge and placement, then handle the full installation.

We also install glass tabletops, shelves and custom shower doors. Tap Learn more to get a free quote.""",
"Learn more", B+"/service/interior/", "hg13-custom-mirrors", "",
"Real photo of a large custom bathroom mirror installed by the team.", ""),

("HG-14", 7, "2026-12-17", "Local", "Update", "Holiday glass check", "glass repair Rio Grande Valley", "",
"""Getting your home ready for holiday guests in the Valley?

Take a quick walk around: check for chipped tabletops, cracked mirrors, sliding glass doors that stick, and windows that do not seal properly. Small issues are usually faster and less expensive to fix before they spread.

Harlingen Glass & Mirror has helped Harlingen families get their homes ready for the holidays for more than 45 years. Tap Learn more to book a repair.""",
"Learn more", B+"/service/residential/", "hg14-holiday-glass-check", "",
"Photo of a clean living room with a sliding glass door or a repaired tabletop.", ""),

("HG-15", 8, "2026-12-22", "FAQ", "Update", "Warranty", "glass installation warranty", "",
"""FAQ: Does Harlingen Glass & Mirror offer a warranty?

Yes. Many of the products we install carry a manufacturer warranty of up to 3 years, and we provide a 1-year installation warranty on specific products. Our team will explain the coverage that applies to your project before we start.

We hold ourselves to a high standard, from sales and service to installation and warranty. Tap Learn more to see why the Valley has trusted us since 1978.""",
"Learn more", B+"/company/", "hg15-faq-warranty", "",
"Photo of an installer finishing a project, or a completed install close-up.", "Confirm current warranty terms with the client."),

("HG-16", 8, "2026-12-29", "Local", "Update", "Year-end thank you", "Harlingen Glass and Mirror", "",
"""As the year comes to a close, thank you to everyone in Harlingen and across the Rio Grande Valley who chose a family-owned local shop for their glass projects.

From shower enclosures and window replacements to storefronts and school security film, it has been a busy year for our team.

If we worked on your home or business this year, we would love to hear how it went. Your feedback helps your neighbors find a glass company they can trust. Tap Learn more to see our work.""",
"Learn more", B+"/company/", "hg16-year-end-thanks", "",
"Collage of 3 to 4 real projects from the year.", "Review request is allowed. Do not offer anything in return for reviews."),

("HG-17", 9, "2027-01-05", "Service", "Update", "Energy-efficient Low-E windows", "energy efficient windows Harlingen", "",
"""New year, lower energy bills. Old or poorly sealed windows let cool air out in summer and warm air out in winter, which makes your AC work harder.

Harlingen Glass & Mirror installs energy-efficient replacement windows, including Low-E glass that helps reduce heat and UV coming into your home without blocking natural light.

Book a free window inspection and we will show you where you can save. Tap Learn more to get started.""",
"Learn more", B+"/service/residential-window-replacement/", "hg17-low-e-windows", "",
"Real photo of new Low-E windows on a Valley home.", ""),

("HG-18", 9, "2027-01-07", "Promotional", "Offer", "Window offer (New Year)", "window replacement deal", "New Year Window Offer: 4th Window Free",
"""Start the year with a home upgrade. Buy 3 windows and get the 4th window free from Harlingen Glass & Mirror.

Energy-efficient windows can help lower your utility bills, make rooms more comfortable and boost curb appeal. Every project includes a free window inspection and a clear quote. Financing is available.

Tap View offer to schedule your free inspection.""",
"View offer", B+"/service/residential-window-replacement/", "hg18-new-year-window-offer",
"Offer dates: Jan 7 to Jan 31, 2027 (confirm the offer is extended). Terms: same as HG-02.",
"Exterior photo of a home with new windows.", "Only publish if the client extends the offer into January."),

("HG-19", 10, "2027-01-12", "FAQ", "Update", "Repair or replace a cracked window", "cracked window repair", "",
"""FAQ: Should I repair a small crack in my window or replace the glass?

A small crack can spread with temperature changes, wind and everyday use, and it can weaken the whole pane. In most cases, replacing the damaged glass is the safer long-term fix, and it is often quicker than people expect.

Our team will look at the damage and tell you honestly what makes sense. Tap Learn more to read our guide and book a visit.""",
"Learn more", B+"/blog/dont-let-a-small-crack-turn-into-a-big-problem/", "hg19-faq-cracked-window", "",
"Close-up of a cracked window pane (own photo).", ""),

("HG-20", 10, "2027-01-14", "Service", "Update", "Fire-rated and bullet-resistant glass", "bullet resistant glass Texas", "",
"""Some businesses need more than standard glass. Banks, clinics, offices and government buildings often require fire-rated or bullet-resistant glass to meet safety standards.

Harlingen Glass & Mirror supplies and installs fire-rated glass, bullet-resistant glass barriers, thermal glazing and glass railing systems for commercial projects across South Texas.

Tap Learn more to talk to our commercial team about your project.""",
"Learn more", B+"/service/commercial-glass/", "hg20-fire-bullet-resistant", "",
"Real photo of a commercial reception window or glass railing project.", "Confirm the bullet-resistant ratings the team installs before adding specifics."),

("HG-21", 11, "2027-01-19", "Local", "Update", "Cold fronts in the Valley", "window seal repair Harlingen", "",
"""Cold fronts in the Rio Grande Valley are a good reminder to check your windows and doors.

If you feel a draft, see gaps around the frame or notice fog between the panes, your windows may not be sealing properly. Fixing them now keeps your home comfortable and helps before the summer heat returns.

Harlingen Glass & Mirror serves homeowners across Harlingen and the Valley. Tap Learn more to book a free assessment.""",
"Learn more", B+"/service/residential/", "hg21-cold-front-check", "",
"Photo of a technician checking a window frame.", ""),

("HG-22", 11, "2027-01-21", "Service", "Update", "Glass tabletops and shelves", "glass tabletop Harlingen", "",
"""Protect your wood furniture or update a room with a custom glass tabletop or glass shelves.

Harlingen Glass & Mirror cuts glass to your exact size and shape, with clean, polished edges for homes, offices and restaurants. We also replace broken tabletops and shelves.

Tap Learn more to get a free quote from your local one-stop custom glass shop.""",
"Learn more", B+"/service/interior/", "hg22-glass-tabletops", "",
"Real photo of a custom glass tabletop on a dining table.", ""),
]
