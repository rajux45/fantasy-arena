import { Nav } from '@/components/Nav';

export default function PrivacyPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8 prose prose-invert">
        <h1>Privacy policy</h1>
        <p>Last updated: 2026-05-01</p>
        <h2>What we collect</h2>
        <ul>
          <li>Account: email / phone / name / DOB (for age check).</li>
          <li>KYC: PAN, masked Aadhaar, address proof — encrypted at rest with AES-256.</li>
          <li>Wallet: ledger entries with monetary amounts in paise.</li>
          <li>Activity: device, IP (geo-block), session start/end, contests joined.</li>
        </ul>
        <h2>How we use it</h2>
        <ul>
          <li>Compliance (KYC, AML, GST, TDS).</li>
          <li>Fraud detection (multi-account, IP velocity, device fingerprints).</li>
          <li>Service operations (showing you matches, leaderboards, balance).</li>
          <li>Anonymized aggregate analytics.</li>
        </ul>
        <h2>What we don&apos;t do</h2>
        <ul>
          <li>Sell or share PII with advertisers.</li>
          <li>Use casino coin balances as a real-money signal — they are virtual.</li>
          <li>Profile minors (we reject under-18 signups at KYC).</li>
        </ul>
        <h2>Your rights</h2>
        <p>Email <a href="mailto:privacy@fantasy-arena.in">privacy@fantasy-arena.in</a> for export, correction, or deletion. Deletion happens within 30 days unless retained for tax/AML compliance (up to 7 years).</p>
        <h2>Security</h2>
        <ul>
          <li>Passwords stored as bcrypt hashes (cost factor 12).</li>
          <li>Sessions are signed JWTs with 1h access + 30d refresh.</li>
          <li>PII encrypted at rest with rotated KMS keys.</li>
          <li>All traffic over TLS 1.3.</li>
          <li>Quarterly penetration tests.</li>
        </ul>
      </main>
    </>
  );
}
