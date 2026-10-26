import sys, datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from openpyxl.worksheet.properties import PageSetupProperties

FONT = "Arial"
F = Font(name=FONT, size=10)
FB = Font(name=FONT, size=10, bold=True)
FT = Font(name=FONT, size=14, bold=True)
FS = Font(name=FONT, size=10, italic=True, color="595959")
HFILL = PatternFill("solid", fgColor="F2F2F2")
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top")
WRAPC = Alignment(wrap_text=True, vertical="top", horizontal="center")


def title(ws, text, sub):
    ws["A1"] = text; ws["A1"].font = FT
    ws["A2"] = sub; ws["A2"].font = FS
    ws.sheet_view.showGridLines = False


def table(ws, row, headers, rows, widths, center_cols=(), col0=1):
    for j, h in enumerate(headers, col0):
        c = ws.cell(row=row, column=j, value=h)
        c.font = FB; c.fill = HFILL; c.border = BOX; c.alignment = WRAP
    for i, r in enumerate(rows, 1):
        for j, v in enumerate(r, col0):
            c = ws.cell(row=row + i, column=j, value=v)
            c.font = F; c.border = BOX
            c.alignment = WRAPC if j in center_cols else WRAP
    for j, w in enumerate(widths, col0):
        if w:
            ws.column_dimensions[get_column_letter(j)].width = w
    return row + len(rows)


def build(cfg, posts, out):
    wb = Workbook()
    # ---------------- Overview ----------------
    ws = wb.active; ws.title = "Overview"
    title(ws, f"{cfg['name']}: GBP Content Calendar and Citations", "22 Google Business Profile posts in 11 weekly batches, plus citation work. Prepared Oct 26, 2026.")
    r = 4
    ws.cell(row=r, column=1, value="Business snapshot (from the website)").font = FB
    snap = cfg["snapshot"]
    r = table(ws, r + 1, ["Field", "Value", "Source / note"], snap, [30, 70, 55])
    r += 2
    ws.cell(row=r, column=1, value="Tracking settings (edit here, all CTA links update)").font = FB
    r += 1
    trk = [("UTM source", "google", "Keep as google"), ("UTM medium", "organic", "Keep as organic"),
           ("UTM campaign", cfg["campaign"], "One campaign for this 22-post run"),
           ("Website domain", cfg["domain"], "Used by the QA check that every link stays on the business website")]
    hdr = r
    table(ws, r, ["Setting", "Value", "Note"], trk, [30, 70, 55])
    cfg["cell_src"], cfg["cell_med"], cfg["cell_camp"], cfg["cell_dom"] = (f"Overview!$B${hdr+1}", f"Overview!$B${hdr+2}", f"Overview!$B${hdr+3}", f"Overview!$B${hdr+4}")
    r = hdr + len(trk) + 2
    ws.cell(row=r, column=1, value="Post mix (counts update from the calendar)").font = FB
    r += 1
    cats = ["Service", "FAQ", "Local", "Promotional"]
    mix_rows = [(c, f'=COUNTIF(\'Content Calendar\'!$E$5:$E$26,"{c}")', f'=IFERROR(B{r+1+i}/B{r+1+len(cats)},0)') for i, c in enumerate(cats)]
    mix_rows.append(("Total", f"=SUM(B{r+1}:B{r+len(cats)})", f"=SUM(C{r+1}:C{r+len(cats)})"))
    end = table(ws, r, ["Category", "Posts", "Share"], mix_rows, [30, 70, 55])
    for rr in range(r + 1, end + 1):
        ws.cell(row=rr, column=3).number_format = "0%"
        ws.cell(row=rr, column=2).alignment = Alignment(horizontal="left", vertical="top")
        ws.cell(row=rr, column=3).alignment = Alignment(horizontal="left", vertical="top")
    ws.cell(row=end, column=1).font = FB
    r = end + 2
    ws.cell(row=r, column=1, value="How to use this workbook").font = FB
    howto = [
        ("1. Overview", "Business facts, tracking settings and the post mix."),
        ("2. Website & Profile Audit", "What we found on the website, socials and old GBP posts, with fixes to make before posting."),
        ("3. GBP Guidelines", "Google rules every post follows, with sources."),
        ("4. Content Calendar", "All 22 posts: date, type, copy, CTA button and tracked link. Edit only Post Copy, dates, Status and Notes."),
        ("5. Weekly Batches", "One batch per week (2 posts). Prep and schedule each batch on the Monday."),
        ("6. Citations", "NAP to use everywhere, plus the citation list with status tracking."),
        ("7. QA Cross-Check", "Automatic checks on every post (length, no phone or email in text, CTA, UTM, link domain). All rows should read Pass."),
        ("Editable cells", "Status and Notes columns, post dates, post copy, citation Status / Date / Live URL. Tracked URLs, counts and QA cells are formulas: do not overwrite."),
        ("Example row", "Row 5 of the Content Calendar (post 01) shows the expected format for every column."),
    ]
    table(ws, r + 1, ["Tab / item", "What it is"], howto, [30, 70, 55])
    ws.freeze_panes = "A4"

    # ---------------- Audit ----------------
    wa = wb.create_sheet("Website & Profile Audit")
    title(wa, "Website, social media and GBP audit", "Checked Oct 26, 2026. Fix High priority items before the first post goes live.")
    table(wa, 4, ["#", "Area", "Finding", "Evidence (URL)", "Recommended action", "Priority"],
          [(i + 1,) + tuple(a) for i, a in enumerate(cfg["audit"])], [5, 18, 55, 45, 50, 10], center_cols=(1, 6))
    wa.freeze_panes = "A5"

    # ---------------- Guidelines ----------------
    wg = wb.create_sheet("GBP Guidelines")
    title(wg, "Google Business Profile post rules applied to this calendar", "Every post in the calendar was written and checked against these rules.")
    table(wg, 4, ["#", "Rule", "How this calendar follows it", "Source"],
          [(i + 1,) + tuple(g) for i, g in enumerate(GUIDE)], [5, 45, 60, 55], center_cols=(1,))
    wg.freeze_panes = "A5"

    # ---------------- Calendar ----------------
    wc = wb.create_sheet("Content Calendar")
    title(wc, "GBP Content Calendar: 22 posts", "Tracked CTA URL is built by formula from the landing page and the Overview tracking settings.")
    heads = ["Post ID", "Batch", "Publish Date", "Day", "Category", "GBP Post Type", "Topic", "Target Keyword",
             "Offer Title", "Post Copy", "Characters", "CTA Button", "Landing Page", "UTM Content",
             "Tracked CTA URL", "Offer Dates / Terms", "Image Brief", "Status", "Notes / Confirm with Client"]
    widths = [9, 7, 12, 8, 12, 11, 26, 26, 26, 70, 10, 11, 42, 24, 60, 34, 34, 13, 34]
    rows = []
    for k, p in enumerate(posts):
        rr = 5 + k
        pid, batch, date, cat, typ, topic, kw, otitle, copy, cta, land, utm, terms, img, notes = p
        d = dt.datetime.strptime(date, "%Y-%m-%d")
        rows.append([pid, batch, d, f'=TEXT(C{rr},"ddd")', cat, typ, topic, kw, otitle, copy.strip(), f"=LEN(J{rr})",
                     cta, land, utm,
                     f'=M{rr}&"?utm_source="&{cfg["cell_src"]}&"&utm_medium="&{cfg["cell_med"]}&"&utm_campaign="&{cfg["cell_camp"]}&"&utm_content="&N{rr}',
                     terms, img, "Draft", notes])
    table(wc, 4, heads, rows, widths, center_cols=(1, 2, 3, 4, 11, 18))
    for k in range(len(posts)):
        rr = 5 + k
        wc.cell(row=rr, column=3).number_format = "mmm d, yyyy"
        wc.row_dimensions[rr].height = 150
    dv = DataValidation(type="list", formula1='"Draft,Client review,Approved,Scheduled,Live,Rejected"', allow_blank=True)
    wc.add_data_validation(dv); dv.add("R5:R26")
    wc.freeze_panes = "C5"
    wc.auto_filter.ref = "A4:S26"

    # ---------------- Weekly batches ----------------
    wbt = wb.create_sheet("Weekly Batches")
    title(wbt, "Weekly batch plan", "Each batch = 2 posts. Content goes to the client 2 working days before the batch week, then is scheduled on the Monday. Batch 8 covers the two holiday weeks (Dec 22 and Dec 29).")
    batches = sorted({p[1] for p in posts})
    brs = []
    for i, b in enumerate(batches):
        rr = 5 + i
        first = min(dt.datetime.strptime(p[2], "%Y-%m-%d") for p in posts if p[1] == b)
        monday = first - dt.timedelta(days=first.weekday())
        brs.append([b, monday, ", ".join(p[0] for p in posts if p[1] == b),
                    f"=COUNTIF('Content Calendar'!$B$5:$B$26,A{rr})",
                    f"=COUNTIFS('Content Calendar'!$B$5:$B$26,A{rr},'Content Calendar'!$E$5:$E$26,\"Service\")",
                    f"=COUNTIFS('Content Calendar'!$B$5:$B$26,A{rr},'Content Calendar'!$E$5:$E$26,\"FAQ\")",
                    f"=COUNTIFS('Content Calendar'!$B$5:$B$26,A{rr},'Content Calendar'!$E$5:$E$26,\"Local\")",
                    f"=COUNTIFS('Content Calendar'!$B$5:$B$26,A{rr},'Content Calendar'!$E$5:$E$26,\"Promotional\")",
                    f"=WORKDAY(B{rr},-2)", "Not started"])
    end = table(wbt, 4, ["Batch", "Week Of (Mon)", "Posts in Batch", "Posts", "Service", "FAQ", "Local", "Promotional", "Content Due to Client", "Batch Status"],
                brs, [8, 14, 22, 8, 9, 8, 8, 12, 18, 14], center_cols=(1, 2, 4, 5, 6, 7, 8, 9, 10))
    tot = end + 1
    wbt.cell(row=tot, column=1, value="Total").font = FB
    for col in "DEFGH":
        c = wbt[f"{col}{tot}"]; c.value = f"=SUM({col}5:{col}{end})"; c.font = FB; c.border = BOX; c.alignment = WRAPC
    for i in range(len(batches)):
        wbt.cell(row=5 + i, column=2).number_format = "mmm d, yyyy"
        wbt.cell(row=5 + i, column=9).number_format = "mmm d, yyyy"
    dv2 = DataValidation(type="list", formula1='"Not started,Drafted,Client review,Scheduled,Done"', allow_blank=True)
    wbt.add_data_validation(dv2); dv2.add(f"J5:J{end}")
    wbt.freeze_panes = "A5"
    cfg["_batch_rows"] = (5, end)

    # ---------------- Citations ----------------
    wct = wb.create_sheet("Citations")
    title(wct, "Citation work", "Use the NAP below exactly, character for character, on every listing.")
    nap_end = table(wct, 4, ["NAP field", "Use exactly"], cfg["nap"], [0, 0], col0=2)
    wct.merge_cells(start_row=4, start_column=3, end_row=4, end_column=5)
    for rr in range(5, nap_end + 1):
        wct.merge_cells(start_row=rr, start_column=3, end_row=rr, end_column=5)
        wct.row_dimensions[rr].height = 30 if len(str(wct.cell(row=rr, column=3).value)) > 60 else 15
    wct.row_dimensions[nap_end].height = 45
    start = nap_end + 3
    wct.cell(row=start - 1, column=2, value="Citation list").font = FB
    crow = [(i + 1,) + tuple(c) + ("Not started", "", "") for i, c in enumerate(cfg["citations"])]
    cend = table(wct, start, ["#", "Platform", "Type", "Priority", "Where to claim / submit", "Current Status (Oct 26)", "Issue / Note", "Action",
                              "Work Status", "Date Done", "Live Listing URL"], crow,
                 [5, 26, 16, 10, 42, 22, 42, 40, 13, 12, 36], center_cols=(1, 4, 9, 10))
    dv3 = DataValidation(type="list", formula1='"Not started,In progress,Submitted,Live,Needs fix"', allow_blank=True)
    wct.add_data_validation(dv3); dv3.add(f"I{start+1}:I{cend}")
    wct.cell(row=cend + 2, column=2, value="Summary").font = FB
    summ = [("Citations listed", f"=COUNTA(B{start+1}:B{cend})"),
            ("High priority", f'=COUNTIF(D{start+1}:D{cend},"High")'),
            ("Live", f'=COUNTIF(I{start+1}:I{cend},"Live")'),
            ("Needs fix", f'=COUNTIF(I{start+1}:I{cend},"Needs fix")'),
            ("Not started", f'=COUNTIF(I{start+1}:I{cend},"Not started")')]
    for i, (a, b) in enumerate(summ):
        rr = cend + 3 + i
        c = wct.cell(row=rr, column=2, value=a); c.font = F; c.border = BOX
        c = wct.cell(row=rr, column=3, value=b); c.font = F; c.border = BOX; c.alignment = Alignment(horizontal="left")
    wct.freeze_panes = wct.cell(row=start + 1, column=3)

    # ---------------- QA ----------------
    wq = wb.create_sheet("QA Cross-Check")
    title(wq, "QA cross-check (automatic)", "Formulas re-check every post when copy or links change. Every row should read Pass before scheduling.")
    qh = ["Post ID", "Max 1,500 chars", "No phone number in text", "No email in text", "No link in text", "CTA button set",
          "UTM on CTA link", "Link on business website", "Offer title max 58 chars", "Category set", "Overall"]
    qrows = []
    for k in range(len(posts)):
        s = 5 + k
        C = f"'Content Calendar'!"
        J = f"{C}J{s}"
        qrows.append([f"={C}A{s}",
                      f'=IF(LEN({J})<=1500,"Pass","Fail")',
                      f'=IF(SUMPRODUCT(--ISNUMBER(SEARCH({{{cfg["phone_tokens"]}}},{J})))=0,"Pass","Fail")',
                      f'=IF(ISNUMBER(SEARCH("@",{J})),"Fail","Pass")',
                      f'=IF(OR(ISNUMBER(SEARCH("http",{J})),ISNUMBER(SEARCH("www.",{J})),ISNUMBER(SEARCH(".com",{J}))),"Fail","Pass")',
                      f'=IF(LEN({C}L{s})>0,"Pass","Fail")',
                      f'=IF(AND(ISNUMBER(SEARCH("utm_source=google",{C}O{s})),ISNUMBER(SEARCH("utm_content=",{C}O{s}))),"Pass","Fail")',
                      f'=IF(ISNUMBER(SEARCH({cfg["cell_dom"]},{C}M{s})),"Pass","Fail")',
                      f'=IF({C}F{s}="Offer",IF(AND(LEN({C}I{s})>0,LEN({C}I{s})<=58),"Pass","Fail"),"N/A")',
                      f'=IF(OR({C}E{s}="Service",{C}E{s}="FAQ",{C}E{s}="Local",{C}E{s}="Promotional"),"Pass","Fail")',
                      f'=IF(COUNTIF(B{s}:J{s},"Fail")=0,"Pass","Fail")'])
    qend = table(wq, 4, qh, qrows, [9, 12, 14, 12, 12, 12, 12, 14, 14, 11, 10], center_cols=tuple(range(1, 12)))
    wq.cell(row=qend + 2, column=1, value="Posts passing").font = FB
    c = wq.cell(row=qend + 2, column=2, value=f'=COUNTIF(K5:K{qend},"Pass")&" of "&COUNTA(A5:A{qend})'); c.font = FB
    wq.cell(row=qend + 3, column=1, value="Note").font = F
    wq.cell(row=qend + 3, column=2, value="The phone check looks for the business phone digits and area code. The link check flags any URL written into the post text: links belong only in the CTA button.").font = FS
    wq.freeze_panes = "B5"

    for s in wb.worksheets:
        s.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        s.page_setup.orientation = "landscape"
        s.page_setup.fitToWidth = 1
        s.page_setup.fitToHeight = 0
    wb.save(out)


GUIDE = [
    ("No phone numbers in post text.", "No post contains a phone number. Calls are tracked through the GBP Call button and Performance report instead.", "https://support.google.com/business/answer/7213077"),
    ("Google may remove posts that contain unverified contact info such as email addresses or social media handles.", "No emails or social handles are written in any post.", "https://support.google.com/business/answer/7213077"),
    ("Posts may not include links to websites not related to the business (Oct 2026 policy update).", "Every CTA links to a page on the business's own website. No links are written in the post text.", "https://www.relevantaudience.com/seo/google-business-profile-policy-bans-promotions-in-listings/ (reporting Google's Oct 6, 2026 update)"),
    ("Offer posts need a title and start and end dates; coupon code, link and terms are optional. Offers get an automatic View offer button.", "All Offer posts have a title of 58 characters or fewer, dates and terms in the Offer Dates / Terms column.", "https://support.google.com/business/answer/7342169"),
    ("Update posts can carry one action button with a link (book, order online, learn more and similar).", "Every Update post has one CTA button with a tracked link.", "https://support.google.com/business/answer/7342169"),
    ("Post descriptions are limited to 1,500 characters.", "All posts are well under the limit; the QA tab checks this automatically.", "GBP post editor limit (Google Business Profile Manager)"),
    ("Posts older than 6 months are archived unless a date range is set.", "Fresh posts go out twice a week so the profile always shows recent content.", "https://support.google.com/business/answer/7342169"),
    ("Content must be relevant to the business and not low quality (no gibberish, misspellings or irrelevant content).", "Every post is about a real service, FAQ, local topic or offer taken from the website.", "https://support.google.com/business/answer/3038177"),
    ("Promotions must clearly state their terms.", "Each offer lists dates and terms to confirm with the client before publishing.", "https://support.google.com/business/answer/3038177"),
    ("Do not ask for personal or confidential information.", "CTAs send users to the website contact or booking pages; posts never ask for personal data.", "https://support.google.com/business/answer/3038177"),
    ("You are responsible for making sure post content complies with applicable laws.", "Claims are limited to facts stated on the website. Items needing client confirmation are flagged in Notes.", "https://support.google.com/business/answer/7213077"),
    ("Photos must follow the photo and video policy (real, relevant, no added text-heavy overlays).", "Image briefs ask for real project photos, not stock images.", "https://support.google.com/business/answer/7213077"),
]
