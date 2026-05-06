# Feature Matrix

Track of features scaffolded in this repo. ✅ = working code path. 🟡 = scaffolded, needs vendor key. 🔒 = behind feature flag / future work.

---

## Auth & Identity (15)
1. ✅ Email + password signup
2. ✅ Phone + OTP signup
3. 🟡 Google OAuth (provider-side keys needed)
4. ✅ JWT access + refresh tokens
5. ✅ Logout / token revocation
6. ✅ Forgot-password reset flow
7. ✅ Email verification
8. ✅ Phone verification (OTP) — sandbox
9. 🟡 KYC: Aadhaar e-KYC (Digio / HyperVerge)
10. 🟡 KYC: PAN verification (NSDL)
11. 🟡 KYC: Selfie liveness
12. ✅ KYC status state machine
13. ✅ Profile management (avatar, name, address)
14. ✅ Account deletion (GDPR/DPDP)
15. ✅ 2FA TOTP for admin

## Wallet & Money (15)
16. ✅ Three-pocket wallet (deposit / winnings / bonus)
17. 🟡 Razorpay deposit (sandbox)
18. 🟡 Cashfree deposit (sandbox)
19. ✅ Withdrawal request → admin queue → payout
20. 🟡 Penny-drop bank-account verification
21. ✅ Transaction history with filters
22. ✅ Statement PDF export
23. ✅ Bonus credit via promo code
24. ✅ Promo code validation engine
25. ✅ Cashback rules (`cashback_engine.py`)
26. ✅ TDS deduction (Sec 194BA, 30%)
27. ✅ GST on entry-fee (28%)
28. ✅ Double-entry ledger + invariant checker
29. ✅ Idempotency keys on payments
30. ✅ Reconciliation job (Celery beat)

## Fantasy — Common (10)
31. ✅ Match listing per sport with status (upcoming/live/completed)
32. ✅ Match detail (lineups, conditions, venue)
33. ✅ Player listing with credits + stats
34. ✅ Team builder validator (composition + credit budget)
35. ✅ Captain 2× / Vice-Captain 1.5× multipliers
36. ✅ Multi-team support (up to 20 teams per user per match)
37. ✅ Lineup-lock at deadline
38. ✅ Edit team before lock
39. ✅ Auto-fill empty contest slots (optional toggle)
40. ✅ Late-join handling

## Fantasy — Cricket (10)
41. ✅ Cricket scoring engine (T20/ODI/Test rules)
42. ✅ Run / boundary / six bonus
43. ✅ Strike-rate bonus + duck penalty
44. ✅ Wicket / maiden over / economy bonus / penalty
45. ✅ Catch / stumping / direct-hit run-out
46. ✅ Player-of-the-match bonus
47. ✅ Live polling adapter for fixture API
48. ✅ Last-2-overs power-play boost (configurable)
49. ✅ Substitute / impact-player handling
50. ✅ DLS-truncated match handling

## Fantasy — Football (10)
51. ✅ Football scoring engine
52. ✅ Goal / assist / clean-sheet / save
53. ✅ Yellow / red card penalties
54. ✅ Penalty saved / missed
55. ✅ Tackles + passes accuracy bonus
56. ✅ Captain / VC multipliers
57. ✅ Position-specific multipliers (GK / DEF / MID / FWD)
58. ✅ Star-player bonus
59. ✅ Match-result handling (full-time vs ET vs penalty)
60. ✅ Late substitute handling

## Fantasy — Kabaddi (10)
61. ✅ Kabaddi scoring engine
62. ✅ Raid / touch / bonus / super-raid
63. ✅ Tackle / super-tackle / high-5
64. ✅ All-out bonus
65. ✅ Defender / raider position weights
66. ✅ Captain / VC multipliers
67. ✅ Substitution handling
68. ✅ Tied-match handling
69. ✅ Star-player bonus
70. ✅ Live PKL adapter stub

## Fantasy — Basketball (10)
71. ✅ Basketball scoring engine
72. ✅ Points / 3-pointers / FT
73. ✅ Rebounds + assists
74. ✅ Steals + blocks
75. ✅ Turnovers / fouls penalty
76. ✅ Double-double / triple-double bonus
77. ✅ Captain / VC multipliers
78. ✅ Position-specific weights
79. ✅ OT handling
80. ✅ DNP handling

## Contests & Leaderboard (10)
81. ✅ Public contests (Mega / H2H / Small / Practice)
82. ✅ Private contests with shareable code
83. ✅ Guaranteed contests (auto-fill empty slots)
84. ✅ Multi-entry vs single-entry contests
85. ✅ Confirmed-prize-pool logic
86. ✅ Live leaderboard via WebSocket
87. ✅ Final leaderboard + rank-tie-breakers
88. ✅ Prize-distribution config (% slabs)
89. ✅ Auto-payout on completion
90. ✅ Refund on cancelled match

## Casino (Play-Money) (15)
91. ✅ Provably-fair seed system (commit-reveal HMAC-SHA256)
92. ✅ Coin packages purchase (₹ → coins)
93. ✅ Crash multiplier game
94. ✅ Plinko 8 / 12 / 16 rows
95. ✅ Mines (3×3 / 5×5)
96. ✅ Dice (over/under)
97. ✅ Roulette (European)
98. ✅ Slots (3 themes, 5 reels × 3 rows)
99. ✅ Blackjack (single-deck)
100. ✅ Game history with seed verification
101. ✅ Casino-wide leaderboard
102. ✅ Daily missions
103. ✅ VIP levels (Bronze→Diamond) with rakeback in coins
104. ✅ Daily login bonus
105. ✅ Hard-coded NO cash-out invariant

## Social & Engagement (15)
106. ✅ Friend invite + referral code
107. ✅ Referral commission (1st-deposit + lifetime % of GGR)
108. ✅ Private contest chat
109. ✅ In-app notification centre
110. 🟡 Push notifications (FCM)
111. 🟡 Email notifications (Postmark / SES)
112. 🟡 SMS notifications (MSG91)
113. ✅ Match reminders
114. ✅ Daily check-in streak rewards
115. ✅ Achievement badges
116. ✅ User XP + level progression
117. ✅ Weekly / monthly / all-time global leaderboards
118. ✅ Tournaments (multi-day series)
119. ✅ User-to-user follow
120. ✅ User profile public page

## Admin Console (15)
121. ✅ Admin login + 2FA
122. ✅ User management (search, ban, unban, force-logout)
123. ✅ KYC approval queue
124. ✅ Withdrawal approval queue
125. ✅ Match CRUD
126. ✅ Contest CRUD + clone
127. ✅ Player CRUD with credit override
128. ✅ Promo code CRUD
129. ✅ CMS (banners, blog, FAQs)
130. ✅ Notification broadcast
131. ✅ Reports: revenue / GST / TDS / DAU / MAU
132. ✅ Audit logs viewer
133. ✅ Manual wallet adjust (with mandatory reason + audit)
134. ✅ Refund management
135. ✅ Fraud-flag review queue

## Security & Anti-Fraud (10)
136. ✅ Rate limiting (Redis token-bucket)
137. ✅ Device fingerprinting hooks
138. ✅ IP-velocity multi-account detection
139. ✅ Idempotency keys
140. 🟡 hCaptcha on signup / withdrawal
141. ✅ Encrypted PII columns (Aadhaar/PAN at-rest)
142. ✅ PCI-scope minimisation (gateway tokenisation only)
143. ✅ Audit trail
144. ✅ RBAC (super_admin / finance / support / cms / readonly)
145. ✅ Webhook signature verification

## Real-time (5)
146. ✅ WS leaderboard channel
147. ✅ WS live-scores channel
148. ✅ WS casino game-state channel
149. ✅ WS notification channel
150. ✅ Server-sent events fallback

## Compliance (10)
151. ✅ 18+ age gate
152. ✅ Self-exclusion (1/7/30/90/permanent)
153. ✅ Deposit limits (D/W/M)
154. ✅ Time-spent limits + reality-check
155. ✅ State-wise geo block (AS/OD/NL/SK/TG/AP) for fantasy real-money
156. ✅ Mandatory KYC before withdrawal
157. ✅ T&C / Privacy / Refund / Responsible-gaming pages
158. ✅ Game-specific T&C per contest
159. ✅ GST 28% on deposits
160. ✅ TDS 30% on net winnings (Sec 194BA)

## DevEx & Infra (10)
161. ✅ Docker Compose (Postgres, Redis, Mailhog, MinIO)
162. ✅ Backend Dockerfile
163. ✅ GitHub Actions: backend lint + test
164. ✅ GitHub Actions: web lint + typecheck + build
165. ✅ GitHub Actions: mobile typecheck
166. ✅ Alembic migrations + autogenerate
167. ✅ Seed script with realistic demo data
168. 🟡 Sentry error tracking
169. ✅ Structured JSON logs
170. ✅ Health + readiness endpoints

## UX (5)
171. ✅ Dark mode
172. ✅ PWA support
173. ✅ Multi-language (en, hi, hi-IN-Latn)
174. ✅ Mobile + Web parity
175. ✅ Accessibility (a11y) defaults

---

**Total: 175 features tracked.**

Legend
- ✅ Code path implemented in this repo
- 🟡 Scaffolded; needs production vendor credentials to activate
- 🔒 Future / behind feature flag
