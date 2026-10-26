# One-month GBP calendar (Mon to Fri, Nov 2 to Dec 1, 2026) with banner specs.
# base = post ID from the earlier calendar whose copy/CTA/landing is reused; "copy"/"title" override where the date changed.
# banner: tpl, tag, head (use | for line break, *word* = accent), sub, chip, photos (local files), focus (CSS object-position)

HG = [
dict(date="2026-11-02", base="HG-01", title="Cracked or Foggy Window? Residential Glass Repair in Harlingen",
     tpl="split", tag="Residential Glass Repair", head="Cracked Window?|We'll Make It *Clear* Again.", sub="Repair and replacement for Valley homes", chip="Free Estimate", photos=["56_image00008.jpg"], focus="50% 60%"),
dict(date="2026-11-03", base="HG-02", title="Buy 3 Windows, Get the 4th Window Free",
     offer="Offer dates: Nov 3 to Nov 30, 2026 (confirm). Terms: confirm eligible window types, minimum order and whether it combines with financing.",
     tpl="offer", tag="Limited-Time Offer", head="Buy 3 Windows|Get the *4th FREE*", sub="Energy-efficient window replacement", chip="Book a Free Inspection", photos=["53_image00005.jpg"], focus="50% 40%"),
dict(date="2026-11-04", base="HG-03", title="FAQ: Why Is My Double-Pane Window Foggy?",
     tpl="faq", tag="Glass FAQ", head="Why Is My Window|*Foggy* Inside the Glass?", sub="A failed seal is usually the cause, and it can often be fixed without a new frame.", chip="Ask Our Team", photos=["93_unsplash_9EyiD1RRYRs.jpg"], focus="60% 50%"),
dict(date="2026-11-05", base="HG-04", title="Family-Owned in Harlingen Since 1978",
     tpl="local", tag="Harlingen, TX", head="Family-Owned|Since *1978*", sub="45+ years of glass work across the Rio Grande Valley", chip="Meet the Team", photos=["38_McAllen-District-Office-12-04-08-001.jpg"], focus="50% 40%"),
dict(date="2026-11-06", base="HG-05", title="Custom Frameless Shower Enclosures",
     tpl="glass", tag="Bathroom Glass", head="Say Goodbye to|the *Shower Curtain*", sub="Custom frameless, semi-frameless and framed enclosures", chip="Free Bathroom Consultation", photos=["30_IMG_20231208_134141.jpg"], focus="50% 45%"),
dict(date="2026-11-09", base="HG-06", title="FAQ: Frameless vs Semi-Frameless vs Framed Shower Doors",
     tpl="trio", tag="Glass FAQ", head="Which Shower Door|Is *Right* for You?", sub="", chip="Compare Styles", photos=["45_ShowerDoor-scaled.jpg","52_image00004.jpg","31_IMG_20231208_134144.jpg"], labels=["Frameless","Sliding","Semi-Frameless"], focus="50% 45%"),
dict(date="2026-11-10", base="HG-09", title="3M Security Window Film for Texas Schools",
     tpl="split", tag="3M Security Window Film", head="Stronger Glass.|*Safer* Campuses.", sub="TEA-focused installs by a 3M authorized team", chip="Book a Campus Walkthrough", photos=["42_Rio-Hondo-Middle-School-3.jpg"], focus="38% 50%"),
dict(date="2026-11-11", base="HG-21", title="Cold Front Season: Check Your Window Seals",
     tpl="frame", tag="Rio Grande Valley", head="Feel a *Draft*?|Check Your Seals.", sub="Cold front season is the time to catch leaky windows", chip="Free Assessment", photos=["51_image00003.jpg"], focus="50% 50%"),
dict(date="2026-11-12", base="HG-10", title="FAQ: Does Any Security Film Meet School Requirements?",
     tpl="faq", tag="Security Film FAQ", head="Is All Security Film|*Compliant*?", sub="Not always. The film, how it's attached and who installs it all matter.", chip="Free Film Assessment", photos=["16_Harlingen-Middle-School-Screw-Locations-Ext-Doors-011.jpg"], focus="50% 45%"),
dict(date="2026-11-13", base="HG-11", title="Commercial Storefront Glass Repair and Replacement",
     tpl="split", tag="Commercial Glazing", head="First Impressions|Start at *Your Storefront*", sub="Storefronts, entry doors and multi-story glazing", chip="Request an Assessment", photos=["19_IMG_0499-scaled.jpg"], focus="50% 50%"),
dict(date="2026-11-16", base="HG-07", title="Financing Available for Glass Upgrades",
     tpl="glass", tag="Financing Available", head="Upgrade Now,|*Pay Over Time*", sub="Financing options through Synchrony Bank", chip="Ask About Financing", photos=["29_IMG_20231208_134139.jpg"], focus="50% 45%"),
dict(date="2026-11-17", base="HG-13", title="Custom Mirrors for Homes, Gyms and Studios",
     tpl="frame", tag="Custom Mirrors", head="Make Any Room|Feel *Bigger*", sub="Cut to size and installed for homes and businesses", chip="Get a Free Quote", photos=["32_IMG_20231208_134148.jpg"], focus="50% 50%"),
dict(date="2026-11-18", base="HG-15", title="FAQ: What Warranty Does Harlingen Glass Offer?",
     tpl="faq", tag="Glass FAQ", head="Is Your Glass Work|*Under Warranty*?", sub="Up to 3-year manufacturer warranty and a 1-year install warranty on specific products.", chip="See Coverage", photos=["31_IMG_20231208_134144.jpg"], focus="50% 40%"),
dict(date="2026-11-19", base="HG-14", title="Get Your Glass Guest-Ready for Thanksgiving",
     tpl="local", tag="Holiday Ready", head="Guest-Ready Glass|for *Thanksgiving*", sub="Fix chipped tabletops, cracked mirrors and sticky doors", chip="Book a Repair", photos=["27_IMG_20231208_134134.jpg"], focus="50% 45%",
     copy="""Getting your home ready for Thanksgiving guests in the Valley?

Take a quick walk around: check for chipped tabletops, cracked mirrors, sliding glass doors that stick, and windows that do not seal properly. Small issues are usually faster and less expensive to fix before they spread.

Harlingen Glass & Mirror has helped Harlingen families get their homes ready for the holidays for more than 45 years. Tap Learn more to book a repair."""),
dict(date="2026-11-20", base="HG-17", title="Energy-Efficient Low-E Window Replacement",
     tpl="split", tag="Energy-Efficient Windows", head="Lower Bills.|*Cooler* Rooms.", sub="Low-E glass that cuts heat without blocking light", chip="Free Window Inspection", photos=["25_IMG_20200123_141554436-scaled.jpg"], focus="50% 45%",
     copy="""Old or poorly sealed windows let cool air out in summer and warm air out in winter, which makes your AC and heater work harder all year in the Valley.

Harlingen Glass & Mirror installs energy-efficient replacement windows, including Low-E glass that helps reduce heat and UV coming into your home without blocking natural light.

Book a free window inspection and we will show you where you can save. Tap Learn more to get started."""),
dict(date="2026-11-23", base="HG-12", title="Free Security Film Assessment Before Winter Break",
     offer="Offer dates: Nov 23 to Dec 18, 2026 (confirm). Terms: assessment is free; installation quoted separately.",
     tpl="offer", tag="For Schools", head="Free Security Film|*Assessment*", sub="Plan installs during winter break", chip="Schedule a Walkthrough", photos=["47_UTB-Kinesiology-Bldg.jpg"], focus="50% 50%"),
dict(date="2026-11-24", base="HG-20", title="Fire-Rated and Bullet-Resistant Commercial Glass",
     tpl="split", tag="Commercial Safety Glass", head="Glass Built for|*Safety Standards*", sub="Fire-rated, bullet-resistant and thermal glazing", chip="Talk to Our Commercial Team", photos=["39_McAllen-District-Office-12-04-08-002.jpg"], focus="50% 40%"),
dict(date="2026-11-25", base="HG-19", title="FAQ: Repair or Replace a Cracked Window?",
     tpl="faq", tag="Glass FAQ", head="Small Crack Today,|*Big Problem* Tomorrow?", sub="Cracks spread with heat, wind and daily use. Here's when to replace the pane.", chip="Book a Visit", photos=["90_unsplash_cracked.jpg"], focus="50% 50%"),
dict(date="2026-11-26", base="HG-08", title="Happy Thanksgiving from Harlingen Glass & Mirror",
     tpl="thanks", tag="Happy Thanksgiving", head="Thankful for|*Our Valley*", sub="From our family to yours", chip="", photos=["91_team_crop.jpg"], focus="50% 40%"),
dict(date="2026-11-27", base="NEW-HG-BATH", title="Free Bathroom Glass Consultation",
     offer="Offer dates: Nov 27 to Dec 31, 2026 (confirm). Terms: free in-home consultation and quote; no obligation.",
     tpl="beforeafter", tag="Free Consultation", head="Before & *After*", sub="Book a free bathroom glass consultation", chip="Book Free Consultation", photos=["49_before.jpg","48_after.jpg"], focus="50% 50%"),
dict(date="2026-11-30", base="HG-22", title="Custom Glass Tabletops and Shelves",
     tpl="glass", tag="Custom Glass", head="Cut to *Your* Size,|Polished to Perfection", sub="Glass tabletops and shelves for homes and offices", chip="Get a Free Quote", photos=["57_image00009.jpg"], focus="50% 45%"),
dict(date="2026-12-01", base="NEW-HG-SPOT", title="Project Spotlight: Glass Across the Rio Grande Valley",
     tpl="spotlight", tag="Project Spotlight", head="Built Across|the *Valley*", sub="Schools, clinics and public buildings", chip="See Our Projects", photos=["08_45130555_1967058790260758_3379670728264646656_n.jpg","41_Rio-Hondo-Middle-School-2.jpg","46_Spi-Fire-Station-No-1.jpg"], focus="50% 50%"),
]

HG_NEW = {
"NEW-HG-BATH": dict(cat="Promotional", typ="Offer", offer_title="Free Bathroom Glass Consultation",
  copy="""Thinking about a bathroom refresh before the new year? See what a custom glass enclosure can do.

Book a free bathroom consultation with Harlingen Glass & Mirror. We will measure your space, show you frameless, semi-frameless and framed options, and give you a clear quote with no pressure. Financing is available.

Tap View offer to book your free consultation.""",
  cta="View offer", landing="https://harlingenglass.com/service/bathroom-enclosures/", utm="hg-free-bath-consult"),
"NEW-HG-SPOT": dict(cat="Local", typ="Update", offer_title="",
  copy="""From school campuses and clinics to fire stations and public buildings, Harlingen Glass & Mirror has helped build and protect properties across the Rio Grande Valley.

Our commercial team handles storefronts, curtain walls, entry systems, fire-rated glass and multi-story glazing, with the same care we bring to every home project.

Planning a commercial project in the Valley? Tap Learn more to see our work.""",
  cta="Learn more", landing="https://harlingenglass.com/service/commercial-glass/", utm="hg-project-spotlight"),
}

PF = [
dict(date="2026-11-02", base="PF-01", title="Fence Repair After Wind and Storm Damage",
     tpl="split", tag="Fence Repair", head="Storm-Damaged Fence?|We *Rebuild* It.", sub="Repairs and rebuilds across the OKC metro", chip="Free Repair Estimate", photos=["192_unsplash_km_VQEFOV20.jpg"], focus="70% 30%"),
dict(date="2026-11-03", base="PF-04", title="Free On-Site Fence Estimate",
     offer="Offer dates: Nov 3 to Nov 30, 2026. Terms: free estimate within the service area; no obligation.",
     tpl="offer", tag="Free Estimate", head="Your New Fence|Starts *Here*", sub="On-site measure, clear written quote", chip="Book Your Free Estimate", photos=["118_IMG_5913.jpg"], focus="70% 55%"),
dict(date="2026-11-04", base="PF-02", title="FAQ: How Tall Can My Fence Be in OKC?",
     tpl="faq", tag="Fence FAQ", head="How Tall Can|My Fence *Be*?", sub="Up to 8 ft in most OKC yards. 6 ft is the most popular. Always check your HOA.", chip="More Fence FAQs", photos=["84_Stained-Western-Red-Cedar-with-Cap-and-Trim-with-a-1x6-Kickboard.jpg"], focus="50% 50%"),
dict(date="2026-11-05", base="PF-03", title="Fence Installation in Edmond, OK",
     tpl="local", tag="Edmond, OK", head="Edmond's *Fence* Crew", sub="Wood, metal and custom gates for Edmond homes", chip="Free Estimate", photos=["77_IMG_01991-2.jpg"], focus="50% 50%"),
dict(date="2026-11-06", base="PF-05", title="Western Red Cedar Stockade Fences Built in Our Shop",
     tpl="split", tag="Cedar Stockade Fences", head="Real Cedar.|*Steel* Posts.", sub="Panels built by hand in our shop", chip="See Fence Styles", photos=["99_6-tall-Cap-and-Trim-Total-Privacy-Board-on-Board.-.jpeg"], focus="50% 50%"),
dict(date="2026-11-09", base="PF-06", title="FAQ: Should I Repair or Replace My Fence?",
     tpl="faq", tag="Fence FAQ", head="Repair or|*Replace*?", sub="Limited damage: repair. Several leaning posts or failing rails: replace.", chip="Read the Guide", photos=["125_new-vs-old.jpeg"], focus="8% 50%"),
dict(date="2026-11-10", base="PF-07", title="Ameristar Ornamental Iron Fences and Gates",
     tpl="frame", tag="Ornamental Iron", head="Security With|*Curb Appeal*", sub="Ameristar iron fences and custom gates", chip="See Recent Projects", photos=["116_Arched-ornamental-iron-double-gate-custom-Letter-2.jpg"], focus="50% 50%"),
dict(date="2026-11-11", base="PF-13", title="The Best Fence for Oklahoma Wind",
     tpl="diagonal", tag="Oklahoma Weather", head="Built for|*Oklahoma Wind*", sub="Post depth, concrete and the right material", chip="Read the Local Guide", photos=["46_IMG_8799-scaled.jpg"], focus="50% 50%"),
dict(date="2026-11-12", base="PF-10", title="FAQ: Why Do Fence Posts Lean in Oklahoma?",
     tpl="faq", tag="Fence FAQ", head="Why Do Fence Posts|*Lean*?", sub="Clay soil swells and shrinks. We set steel posts in concrete 2 ft below grade.", chip="Read the Article", photos=["41_IMG_5922.jpg"], focus="50% 50%"),
dict(date="2026-11-13", base="PF-09", title="Sheet Metal Fence for Commercial Properties",
     tpl="split", tag="Commercial Fencing", head="Privacy That|*Won't Rot*", sub="Sheet metal and ribbed panel fences for commercial sites", chip="Commercial Estimate", photos=["149_4800-S-Sunnylane-Rd_Completed-Pic-5-scaled.jpg"], focus="50% 50%"),
dict(date="2026-11-16", base="PF-12", title="Add a Custom Doggie Window to Your Fence",
     tpl="glass", tag="Pet-Friendly Add-On", head="A *Window* for|Your Best Friend", sub="Custom doggie windows for any stockade fence", chip="See Doggie Windows", photos=["127_bassethound-doggie-window.jpeg"], focus="50% 95%"),
dict(date="2026-11-17", base="PF-11", title="Chain Link Fencing: Galvanized or Black Vinyl-Coated",
     tpl="frame", tag="Chain Link Fencing", head="Affordable,|*Secure*, Built to Last", sub="Galvanized or black vinyl-coated, with gates", chip="Get a Free Quote", photos=["16_4-black-chain-link.jpg"], focus="50% 50%"),
dict(date="2026-11-18", base="PF-14", title="FAQ: What Is the Most Affordable Fence in OKC?",
     tpl="faq", tag="Fence FAQ", head="What's the Most|*Affordable* Fence?", sub="Galvanized chain link. For wood, Western Red Cedar on metal posts.", chip="Get a Free Estimate", photos=["98_1x4x6-Western-Red-Cedar-with-Cap-and-Trim-scaled.jpg"], focus="50% 50%"),
dict(date="2026-11-19", base="PF-22", title="North OKC Fence Installation and Repair",
     tpl="local", tag="North OKC", head="Hand-Built in Our|*North OKC* Shop", sub="100% USA fence products. 1-year warranty.", chip="Free Estimate", photos=["35_IMG_5879.jpg"], focus="50% 40%"),
dict(date="2026-11-20", base="PF-18", title="Low-Maintenance Vinyl Fence Installation",
     tpl="glass", tag="Vinyl Fencing", head="No Staining.|*No Painting.*", sub="Vinyl privacy, picket and ranch-style fences", chip="See Vinyl Styles", photos=["21_6-tall-white-vinyl-privacy-fence-.jpg"], focus="50% 55%"),
dict(date="2026-11-23", base="PF-17", title="Free Fence Design and Planning Consultation",
     offer="Offer dates: Nov 23 to Dec 31, 2026 (confirm). Terms: consultation and estimate are free; no obligation.",
     tpl="offer", tag="Free Consultation", head="Plan Your Spring|*Fence* Now", sub="Free design and planning consultation", chip="Book Your Consultation", photos=["62_desing-and-planning.jpg"], focus="50% 50%",
     copy="""Thinking about a new fence for spring? Not sure which style, material or height is right for your property?

Book a free design and planning consultation with Preferred Fence Solutions. We will walk your yard, talk through privacy, pets, gates and budget, and recommend the best option for your home before we schedule your install.

Tap View offer to book your consultation."""),
dict(date="2026-11-24", base="PF-15", title="Residential Gates: Width and Placement",
     tpl="split", tag="Custom Gates", head="The Right Gate,|in the *Right Place*", sub="Plan access before the posts go in", chip="Read the Gate Guide", photos=["109_o-3.jpg"], focus="50% 50%"),
dict(date="2026-11-25", base="PF-19", title="FAQ: Will New Cedar Boards Match My Old Fence?",
     tpl="faq", tag="Fence FAQ", head="Will New Boards|*Match* My Old Fence?", sub="Size and style, yes. Color evens out as new cedar weathers.", chip="See What to Expect", photos=["13_1x4x6-Western-Red-Cedar-with-Cap-and-Trim-scaled.jpg"], focus="50% 50%"),
dict(date="2026-11-26", base="PF-08", title="Happy Thanksgiving from Preferred Fence Solutions",
     tpl="thanks", tag="Happy Thanksgiving", head="Thankful for|*Our Neighbors*", sub="From our crew to your family", chip="", photos=["93_o-8.jpg"], focus="50% 50%"),
dict(date="2026-11-27", base="PF-21", title="Free Fence Repair Estimate",
     offer="Offer dates: Nov 27 to Dec 31, 2026. Terms: free estimate within the service area; no obligation.",
     tpl="offer", tag="Free Repair Estimate", head="Leaning or|*Damaged* Fence?", sub="Honest repair-or-replace advice", chip="Book a Free Estimate", photos=["195_unsplash_LbkIbkMPKjg.jpg"], focus="50% 50%",
     copy="""Did fall storms or strong wind leave your fence leaning or damaged?

Book a free fence repair estimate with Preferred Fence Solutions. We will check posts, panels and gates, tell you honestly whether repair or replacement makes more sense, and give you a clear quote. No job is too small.

Tap View offer to schedule your free repair estimate."""),
dict(date="2026-11-30", base="PF-20", title="SimTek Fences: The Look of Stone",
     tpl="diagonal", tag="SimTek Fencing", head="The Look of *Stone*,|Without the Upkeep", sub="SimTek fences for Edmond, OKC, Mustang and Yukon", chip="Is SimTek Right for You?", photos=["194_unsplash_0WxjDT_3Tsw.jpg"], focus="50% 50%"),
dict(date="2026-12-01", base="PF-16", title="Thank You, Oklahoma City",
     tpl="spotlight", tag="Thank You, OKC", head="Award-Winning|*Fence Crew*", sub="Every fence and gate backed by a 1-year warranty", chip="See Our Awards", photos=["36_IMG_5887.jpg","38_IMG_5911.jpg","90_o-2.jpg"], focus="50% 50%",
     copy="""Thank you, Oklahoma City, for another great year.

We are honored to have won local awards for our fencing work, and we stand behind every fence and gate we install with a 1-year warranty. More than any award, we are grateful for customers who welcome our crew into their yards and recommend us to their neighbors.

If we built or repaired your fence this year, we would love to hear how it is holding up. Tap Learn more to see our awards."""),
]
PF_NEW = {}
