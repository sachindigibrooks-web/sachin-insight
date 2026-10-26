# Client revision round v2: captions, creative files and change notes per sheet row.
RAW = "https://raw.githubusercontent.com/sachindigibrooks-web/sachin-insight/claude/happy-albattani-9glwi2/deliverables/mudras/client-revisions-v2/"

def files(folder, names):
    return "\n".join(RAW + folder + "/" + n for n in names)

CAR5 = [f"instagram-carousel-slide-{k}-1080x1350.png" for k in range(1, 6)]

IG = {
 4: dict(files=files("ig-fb/r04-countdown", CAR5),
  caption="""NYC, it's go time. 🗽 6 days left!
Runners, sound off in the comments 👇
Bib number. Goal time. Marathon number #.
We'll be your loudest cheer squad all week. 📣💛
Legs feeling the miles? Book a targeted pre-race session with our specialists before the big day. Link in bio 🔗
#MudrasFam #NYCMarathon #RunNYC #MarathonCountdown #RaceWeek #ChelseaNYC""",
  notes="Slide 1 now says 6 days (for posting on Oct 26; marathon is Sunday, Nov 1). All 5 carousel slides are linked in order, so the dots match. Removed \"quick\" from the caption."),
 5: dict(files="",
  caption="""Deep Tissue Massage: What It Feels Like & How to Prepare

Booking your first deep tissue massage? Here's what to expect:
• It uses slow, firm pressure to reach deeper layers of muscle. Tight areas can feel intense, but it shouldn't feel painful.
• More pressure isn't always better. If you're holding your breath or tensing up, it's too much.
• Tell your specialist your pressure preference before you start, and speak up during the session. Pressure can be adjusted at any time.
• Mild soreness for a day or two afterward can be normal. Drink water and move gently, and let us know if it lasts longer.

Read the full guide 👉 https://www.mudras.com/deep-tissue-massage-nyc

#DeepTissueMassage #DeepTissueMassageNYC #ChelseaNYC #MassageTherapyNYC #MudrasNYC #MassageChelsea #MuscleTension #MassageTherapy""",
  notes="Image kept. The caption now gives the preparation points, explains communicating pressure preferences, and links the full guide."),
 6: dict(files="",
  caption="""Monday and already reaching for the back of your neck? 🙋
Our neck, shoulder & back sessions focus on tension from desk work, travel and repetitive activity, and also look at connected areas that affect how you move.
Evening sessions available, by appointment.
Book 👉 https://calendly.com/hello-mudras
#MudrasNYC #MassageChelsea #ChelseaNYC #NeckAndShoulderMassage #BackMassageNYC #MassageTherapyNYC #TherapeuticMassage""",
  notes="Image kept. Removed the 9pm claim, added \"by appointment\", and the booking line now links the real booking page (calendly.com/hello-mudras)."),
 7: dict(files=files("ig-fb/r07-go-get-it-nyc", ["facebook-feed-1080x1350.png"]),
  caption=None,
  notes="Running image and headline kept. The subline now reads \"Every Mile Deserves Recognition.\" instead of \"Run Today. Recover Tomorrow.\""),
 8: dict(files="",
  caption="""HR and office managers: now scheduling November team wellness sessions. 📅

Give your team a wellness day this month. Mudras offers onsite bodywork at your office or group sessions at our Chelsea studio, shaped around your team's schedule.
Plan your session 👉 https://www.mudras.com/corporate-massage-nyc

#CorporateWellness #HR #NYC""",
  notes="Event photo kept. Removed \"filling up fast\" and \"limited dates left\", and used \"Now scheduling November team wellness sessions.\""),
 9: dict(files=files("ig-fb/r09-sports-or-deep-tissue", ["instagram-feed-1080x1350.png"]),
  caption="""Training for a marathon? Here's how we tailor bodywork to your training.
Sports massage is planned around your training, race date and recovery, and can include deep tissue, stretching and mobility work. These techniques can be combined in one session, so you don't need to pick the right one yourself. Tell us your race date and how your legs feel, and your specialist will adjust pressure and focus, including how much deeper work makes sense close to race day. From Mudras, Chelsea NYC.

#NYCMarathon #SportsMassage #RunnerRecovery #DeepTissueMassage #RunNYC

Link: https://www.mudras.com/massage-for-runners-nyc""",
  notes="Artwork now reads \"How we tailor bodywork to your training\". The caption explains that techniques can be combined. Removed the blanket \"skip deep tissue before a race\" line; a specialist should still review the race-week guidance."),
 10: dict(files=files("ig-fb/r10-lactic-acid-myth", CAR5),
  caption="""MYTH: Massage flushes lactic acid out of your legs.
If you ran on Sunday and your legs feel sore on the stairs today, here's what's really going on 👇
That soreness a day or two after a long run usually isn't leftover lactic acid. It's DOMS (delayed onset muscle soreness), your body's normal response to hard effort.
Massage doesn't flush lactic acid out of your muscles. What it may do is help ease that sore, tight feeling as part of a bigger recovery plan: rest, hydration, good food and gentle movement.
No magic, just good bodywork.
Feeling it on the stairs today? Our post-race sessions adapt pressure and focus to how your legs feel. Link in bio to book.
Save this 📌 and send it to a runner who still believes the lactic acid myth.

#Mudras #MudrasFam #BodyReset #NYCMarathon #MarathonRecovery #DOMS #MythBusting #RunnerTips #SportsMassageNYC #RunNYC #ChelseaNYC #NYCRunners""",
  notes="Removed the large emojis from all slides. Slide 4 now says \"May help ease\". The caption narrows the claim to the lactic-acid myth and replaces \"can barely walk\" with milder wording."),
 11: dict(files=files("ig-fb/r11-finish-line", ["instagram-feed-1080x1350.png"]),
  caption="""Ran yesterday? Cheered for 6 hours? Either way, your legs earned a reset. 🏅
Congratulations to every runner who crossed the finish line, and to every supporter who walked miles across the city to cheer.
Post-race recovery sessions are available this week, by appointment.
✅ Your specialist asks how you're feeling first
✅ Pressure is adjusted to suit your body after the race
✅ Any medical guidance you've had is taken into account
Tell us you ran when you book so we can plan the right session for you.

📍 37 W 20th St, Chelsea
👉 View availability: https://calendly.com/hello-mudras
📞 Or call (212) 837-8382

#NYCMarathon #MarathonRecovery #ChelseaNYC""",
  notes="Headline is now \"The Finish Line Is Only Part of the Story.\" Removed the evening-hours claim and added \"by appointment\". Schedule this post for Nov 2. Please confirm availability that week."),
 12: dict(files=files("ig-fb/r12-prenatal", ["instagram-feed-1080x1350.png"]),
  caption="""Can you get a massage while pregnant? Often, yes, and suitability is assessed individually.
Prenatal sessions are adapted for your stage of pregnancy, with careful positioning, comfortable pressure and support throughout. Share your stage and any guidance from your doctor or midwife when you book, and check with them first if you're unsure. Postnatal massage can support your body in the months after birth too. From Mudras, Chelsea NYC.

#PrenatalMassage #PregnancyNYC #PostnatalCare #NYCMoms #Pregnancy
Link: https://www.mudras.com/pre-postnatal-massage-therapy-nyc""",
  notes="Removed the pointing emoji from the artwork. The caption now answers the question directly and says suitability is assessed individually. Removed the \"at every stage\" promise. Needs prenatal specialist approval."),
 13: dict(files=files("ig-fb/r13-after-work-bodyreset", ["instagram-feed-1080x1350.png"]),
  caption="""Long day at the desk? Shoulders up by your ears? 🙋
Skip the couch scroll and come in for an after-work BodyReset, a short trip from Flatiron and Union Square. Evening sessions by appointment.
📍 37 W 20th St, 6th Floor, Chelsea
⏱️ 60, 90 or 120 minute sessions
👉 View availability: https://calendly.com/hello-mudras
📞 (212) 837-8382
#ChelseaNYC #AfterWork #NYCMassage""",
  notes="Artwork now reads \"After-Work BodyReset Sessions in Chelsea.\", with no hours claim. \"Book tonight\" is now \"View availability\", the caption adds \"by appointment\", and the hours are removed."),
 14: dict(files="", caption=None,
  notes="Checked: the updated caption has no operating hours. Image kept."),
 15: dict(files=files("ig-fb/r15-what-is-a-bodyreset", CAR5),
  caption="""A BodyReset follows you. ✨
You don't need to choose a technique or know where the problem starts. Just tell us what you're feeling, and your specialist builds the session around it:

🔹 Deep tissue
🔹 Trigger point therapy
🔹 Myofascial release
🔹 Neuromuscular techniques
🔹 Assisted stretching
…chosen and combined for your body, that day.

📍 Chelsea, NYC
🔗 Book your BodyReset: https://calendly.com/hello-mudras

#Mudras #BodyReset #BespokeMassage #SecretWeapon #MudrasFam #NYCMassage #MassageTherapyNYC #ChelseaNYC #NYCWellness""",
  notes="Slides are linked in order: cover, Understand, Work With Intention, Adapt Throughout, closing. The final slide adds \"Book your BodyReset · calendly.com/hello-mudras\". Removed \"Most massages follow a routine\"."),
 16: dict(files=files("ig-fb/r16-bodyreset-focus", ["facebook-feed-1080x1350.png"]), caption=None,
  notes="Artwork heading is now \"What a BodyReset Session Can Focus On\". The grid lists treatment priorities instead of results: Releasing tension, Comfortable movement, Breathing patterns, Relaxation & rest."),
 17: dict(files=files("ig-fb/r17-screens-make-time-to-move", ["instagram-feed-1080x1350.png"]),
  caption="""Looking down at your phone right now? 👀

Long hours on phones, laptops and game controllers can leave your neck and shoulders feeling stiff or tense. Taking breaks to move and change positions throughout the day may help you feel more comfortable.

Long Hours on Screens? Make Time to Move. 📱

If tension persists, our specialists offer deep tissue work, trigger point therapy, myofascial release and assisted stretching, tailored to your needs.

📍 Chelsea · by appointment
👉 https://www.mudras.com/neck-shoulder-back-pain-massage-in-nyc

#MudrasMassage #NeckPainRelief #ShoulderTension #MassageTherapy #PostureMatters #NYCMassage #ChelseaNYC #SelfCare""",
  notes="The artwork line \"Phones down, chin up\" is now \"Long Hours on Screens? Make Time to Move.\" Replaced the hours line in the caption with \"by appointment\"."),
 18: dict(files=files("ig-fb/r18-corporate-massage-nyc", ["instagram-feed-1080x1350.png"]), caption=None,
  notes="Rebuilt in the full-width event-photo layout using the high-resolution original (2500px), so the soft and pixelated crop is gone."),
}

LI = {
 4: dict(files=files("linkedin/r04-different-techniques", ["linkedin-single-image-1080x1350.png"]),
  caption="""Deep tissue or myofascial release? You don't have to choose.

Deep tissue work focuses on deeper layers of muscle, using slow, firm pressure on areas of tightness.
Myofascial release focuses on fascia, the connective tissue around your muscles, using gentle, sustained pressure.

Your specialist can combine both in one individualized session, depending on what your body needs that day.
It may suit you if you have:
✔️ Tightness that regular massage hasn't helped
✔️ Restricted movement in your neck, shoulders or back
✔️ Tension from desk work or repetitive movement

👉 https://www.mudras.com/myofascial-release-massage-nyc

#MyofascialRelease #DeepTissue #ChelseaNYC""",
  notes="Removed the down and sideways arrows. The headline is now \"Different Techniques. One Individualized Session.\" The caption explains each technique's focus."),
 5: dict(files=files("linkedin/r05-where-it-hurts", ["linkedin-single-image-1080x1350.png"]),
  caption="""Neck discomfort can involve more than the neck alone.
Hours of sitting, a forward head, rounded shoulders, heavy bags on one side, travel, a laptop on the sofa: these patterns connect. That's why our specialists look at the whole picture, not just the spot that hurts.
At Mudras, neck, shoulder and back sessions combine techniques such as deep tissue work, trigger point therapy, myofascial release and assisted stretching, selected for what the body presents that day.
If discomfort lingers or comes with numbness or tingling, we refer clients to the right medical professional first.
For leaders: how many people on your team are working through this every day?

https://www.mudras.com/neck-shoulder-back-pain-massage-in-nyc
#WorkplaceHealth #EmployeeWellbeing #DeskJob #Wellness""",
  notes="Headline kept. Removed the dotted pathway. The opening line is now \"Neck discomfort can involve more than the neck alone.\" The referral language is kept."),
 6: dict(files="",
  caption="""No two bodies show up the same way, so no two sessions should look the same. That idea is at the heart of the Mudras BodyReset.

Every session starts with a conversation about goals, work, training and how the body feels today. The techniques, pressure and focus follow from that, whether the client is an athlete, a performer or an executive.

Attention to the individual is where the details start to matter.

It's a lesson that goes beyond massage. Where in your business could "bespoke" make the biggest difference?

#Founder #CustomerExperience #SmallBusiness #Wellness #NYC""",
  notes="Image kept. Removed the competitor comparison and the unconfirmed Yotam quote and years claim. The caption is rewritten in the brand voice."),
 7: dict(files=RAW.replace("client-revisions-v2/", "") + "linkedin-behind-every-marathoner/linkedin/linkedin-single-image-1080x1350.png",
  caption="""Someone on your team may be running the TCS New York City Marathon on Sunday, November 1.
They've trained through early mornings, long weekend runs and full workdays, and race week is when a little flexibility can go a long way.

3 simple ways managers can help this week:
🏃 Go easy on late meetings and late-night emails
📣 Plan a team shout-out for Monday after the race
💆 Offer recovery support: a flexible morning, a wellness stipend, or a massage

Small gestures like these show people they're seen as more than their output.
Have a marathoner on your team? Tag them below and wish them luck 👇

👉 https://www.mudras.com/corporate-massage-nyc
#NYCMarathon #EmployeeWellbeing #Leadership #HR #CompanyCulture""",
  notes="Linked the creative \"Behind Every Marathoner Is a Great Manager\". Removed \"usually get the least\" and used the actual race date (Sunday, November 1)."),
 8: dict(files="",
  caption="""Yesterday, runners across New York crossed the finish line of the NYC Marathon.
For a small studio in Chelsea, it's one of the most rewarding weeks of the year. We get to hear the stories behind the miles: first marathons, comebacks after injury, people running for causes close to their hearts.
To every runner, and every company and coach who supported them: congratulations. 💛
This week we're focused on recovery, helping those legs get back to everyday life.

#NYCMarathon #runners #Gratitude #NYC #NewYork""",
  notes="Image kept. The opening line is now \"Yesterday, runners across New York crossed the finish line...\" (unverified claim removed)."),
 9: dict(files=files("linkedin/r09-physical-wellbeing-workday", ["linkedin-single-image-1080x1350.png"]),
  caption="""Hours of sitting and screen time often show up in the neck and shoulders first.

It's one of the most common things we hear from professionals who walk into our Chelsea studio. Back-to-back calls, travel, a laptop on the sofa at 10pm: it adds up.

If you lead a team, it's worth asking how physical wellbeing fits into the workday.

#MudrasNYC #ChelseaNYC #WorkplaceWellness #CorporateWellness #NeckAndShoulderTension #MassageTherapyNYC #DeskJobWellness #OfficeWellness #EmployeeWellbeing #MassageChelsea #NYCProfessionals #StressRelief #MuscleRecovery #WellnessAtWork""",
  notes="Artwork is now \"Make Physical Wellbeing Part of the Workday.\" Removed the \"lagging indicator\" and weeks-of-tension claims, no longer assumes what the reader's program includes, and fixed the missing space before the hashtags."),
}

PIN = {
 4: dict(files=files("pinterest/r04-myofascial-release", ["pinterest-pin-1000x1500.png"]),
  caption="""Myofascial release works on fascia, the connective tissue around your muscles. It uses gentle, sustained pressure to help tight tissue loosen gradually, and it shouldn't be painful. It suits desk-work tension, restricted neck or back movement, and active recovery. From Mudras massage, Chelsea NYC.
https://www.mudras.com/myofascial-release-massage-nyc

#MyofascialRelease #Fascia #MassageTherapy #DeskWorker #NYCMassage""",
  notes="\"Slow, sideways pressure\" is now \"Gentle, sustained pressure\" in both the artwork and the caption. The photo is cropped into the hands, so the window squares in the background are gone."),
 5: dict(files=files("pinterest/r05-neck-shoulder-contributors", ["pinterest-pin-1000x1500.png"]),
  caption="""Why does your neck feel stiff by mid-afternoon? Common contributors include long sitting, phone use, low laptops, heavy bags, slouched posture, travel and gym strain. Simple habits that may help: screen at eye level, movement every 30–45 minutes, and support for your lower back. Plus when to see a massage therapist. Chelsea, NYC.
https://www.mudras.com/neck-shoulder-back-pain-massage-in-nyc

#NeckPain #ShoulderTension #BackPain #PostureTips #DeskWorker""",
  notes="\"Causes\" is now \"Contributors to\". The seven labels are enlarged from 36px to 48px."),
 6: dict(files="",
  caption="""You don't need to be a pro athlete to book a sports massage. 💪

It may be worth considering if:
✅ You're preparing for a race, match or competition
✅ You just finished an event or a tough training block
✅ You're recovering from an injury alongside your physician or PT
✅ Regular training has started to affect how you move day to day

We work with runners, basketball and football players, MMA fighters, dancers and more.
👉 https://www.mudras.com/sports-massage-nyc

#SportsMassage #ChelseaNYC #NYCAthletes #basketballplayers #runners #MMAfighters #dancers #athletes""",
  notes="Image kept. Removed the \"hip, hamstring or shoulder keeps flaring up\" line. The physician/PT line is kept."),
 7: dict(files=files("pinterest/r07-when-sports-massage", ["pinterest-pin-1000x1500.png"]),
  caption="""When should athletes book a sports massage? Timing depends on your training, recovery and goals. Options include sessions in the lead-up to a race or competition (timed with your specialist), after an event or heavy training block, as ongoing maintenance, or during injury recovery alongside your provider. From Mudras sports massage, Chelsea NYC.

https://www.mudras.com/sports-massage-nyc

#SportsMassage #AthleteRecovery #RunnerTips #TrainingTips #NYCFitness""",
  notes="Added the answer line \"Timing depends on your training, recovery and goals.\" to the artwork. The caption no longer implies a pre-event session suits everyone."),
 8: dict(files=files("pinterest/r08-race-week-checklist", ["pinterest-pin-1000x1500.png"]),
  caption="""Running the TCS New York City Marathon? Your race-week checklist: taper your miles, protect your sleep, stick to familiar food, test your gear, plan your route to the start, and plan your post-race recovery. From Mudras sports massage, Chelsea NYC.
https://www.mudras.com/massage-for-runners-nyc

#NYCMarathon #RaceWeek #MarathonTraining #RunNYC #RunnerTips""",
  notes="Removed \"9 days to go\" and enlarged the checklist. \"Book recovery before race day\" is now \"Plan your post-race recovery\". Added the destination link to the caption."),
}
