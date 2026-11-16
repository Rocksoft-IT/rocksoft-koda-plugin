<!-- preview-link -->

**What this delivers:** When a client has more than one repository, Rocksoft
Flow now groups them by client and shows what each one is for. If the
request clearly points to one of them, it goes there without asking; if not,
you'll be asked to pick from a clear, labeled list. When one request needs
work in two repositories of the same client (for example a backend change
and its matching frontend screen), the flow now agrees the split with you,
shows both draft issues together, and — once you confirm — creates both
issues tagged so they show up together as one feature.

**Your decision is needed on:**
- We tag every multi-issue request with the same shared feature id, not just
  requests that split across two repositories of the same client. We think
  this gives the most consistent grouping everywhere a request touches more
  than one repository; tell us if you'd rather limit that tagging to
  same-client splits only, as the original request literally described.

**Status:** Ready to merge; nothing to check by hand.
