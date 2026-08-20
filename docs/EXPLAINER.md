# The project in plain English

*No telecom or coding background needed. If you can picture an exam being graded, you can understand this.*

---

## The one-sentence version
I built a tool that automatically checks whether a 5G mobile network is following the official
rulebook — and it caught a real privacy hole that a quick glance would miss.

---

## The problem (everyday version)
A 5G network is a huge machine with a phone, a cell tower, and a "brain" (the core network) all
talking to each other thousands of times a second. There's an official rulebook — the 3GPP standards
— that says *exactly* how they should talk.

When engineers test the network, they usually record the conversation and then **squint at it by
hand** to see if the rules were followed. That's slow, easy to get wrong, and a small mistake can
slip through and only blow up later in front of real customers.

**Analogy:** it's like a teacher grading 500 exam papers by eye, one at a time, hoping not to miss
anything.

---

## What I built (the exam-grader)
An **automatic grading machine** for the network's conversation.

- The **rulebook** (3GPP standard) = the *answer key*.
- The recorded conversation (a "capture") = the *student's exam paper*.
- My tool = the *grading machine* that reads the paper and marks it against the key — and shows its
  working: **PASS or FAIL, plus the evidence and the exact rule.**

You press one button, it reads the recording, and it tells you: did the network follow the rules?
Yes or no, with proof.

---

## The 5 things it checks (in plain words)
Think of these as 5 questions on the exam:

1. **Did the phone hide its identity properly?** (SUCI) — Your phone shouldn't shout its permanent ID
   over the air; it should send a scrambled version. *Like sealing a letter in an envelope instead of
   writing on a postcard.*
2. **Did the phone and network prove who they are to each other?** (5G-AKA) — A secret handshake, so
   an imposter tower can't trick your phone. *Like a bank confirming it's really you before a transfer.*
3. **Did the phone successfully sign in?** (Registration) — The full "log in to the network" sequence
   completed. *Like a successful login, not a spinning wheel.*
4. **Can real data actually flow?** (PDU session) — A connection opens and data gets through with no
   loss. *Like the Wi-Fi connecting AND actually loading a web page.*
5. **Do the two halves of the tower agree on the network's name?** (SIB1) — If they disagree, the
   phone gets confused and the handshake fails. *Like a form where two pages list your address in a
   different order and the system rejects you.*

---

## The real problem it caught (the money moment)
On check #1, the network *did* send a scrambled ID — so a quick look says "fine, it's scrambled."
But my tool looked closer and found the scrambling was set to **"none."** The envelope was there, but
it was **see-through** — the phone's permanent ID was actually readable in plain sight.

**Analogy:** you asked for your letter in a sealed envelope, and technically you got an envelope —
but it was a clear plastic one. Anyone can read it.

A quick human check passes this. My tool flags it as a **FAIL** and says exactly why. That's the whole
point: it catches the mistakes that *look* fine.

*(Note: this is a lab setup issue, easily fixed by turning real scrambling on — but a leak like this
in the real world would expose people's identities.)*

---

## The clever extra: teaching an offline AI to help — carefully
Writing these grading machines is skilled work. I wanted to see if an **AI that runs completely
offline** (no internet, important for security-sensitive telecom companies) could write them.

So I set up three "graders":
- **A trusted reference grader** (the gold standard).
- **Two offline AI graders**, each fed the rulebook and asked to write their own version.

Then a comparison tool lines up all three answers. Where the AI graders disagree with the trusted one,
it flags it, I fix them, and repeat until all three agree.

**What I learned (the honest, interesting part):** the offline AIs understood *what* to check, but
they **faked the hard parts** — one of them literally invented a fake command to do the cryptography
instead of actually doing it; the other left the hard function blank and even wrote code that wouldn't
run. So the lesson is: **an offline AI is good enough to draft a check, but you can't trust it to be
correct on its own** — you need a reliable reference and a human to keep it honest. That finding is
genuinely useful to any company thinking about using offline AI.

**Analogy:** a smart intern who gives you a confident, well-formatted answer that's wrong in the
details. Useful for a first draft; dangerous if you don't check it.

---

## Why this is valuable (in one breath)
- It turns slow, error-prone manual checking into a **one-button, repeatable test with proof.**
- It **caught a real defect** that surface checks pass.
- It **runs offline**, so a security-strict operator can use it air-gapped.
- It works as a **safety net**: if someone changes a setting and breaks the rules, the tool catches it
  immediately — not months later in the field.

---

## The honest small print (I say this up front, always)
- The "network" here runs as **software on a computer** (a simulator), not real radio hardware.
- The privacy FAIL is a **lab setting**, not a broken phone — but it's the exact *kind* of bug that
  matters in the real world.
- The AI **drafted**; a human **corrected and verified**. The AIs did not fix themselves.

---

## If you remember one thing
It's an **automatic, evidence-based grader for a 5G network** — and it proved its worth by catching a
privacy leak that everyone else's quick check calls "fine."
