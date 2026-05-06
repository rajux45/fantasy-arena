import { Nav } from '@/components/Nav';

export default function LegalPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-3xl px-4 py-8 prose prose-invert">
        <h1>Legal & Responsible Gaming</h1>
        <p>
          Fantasy Arena offers two distinct experiences: <strong>fantasy sports</strong> (skill-based; legal in
          most Indian states under the Public Gambling Act 1867 and various state High Court rulings) and a{' '}
          <strong>play-money social casino</strong> (no real-money cash-out; legally distinct from gambling).
        </p>
        <h2>State restrictions on real-money fantasy</h2>
        <p>Real-money fantasy contests are not available in: AS, OD, NL, SK, TG, AP.</p>
        <h2>18+ only</h2>
        <p>You must be 18+ to use this app, regardless of state.</p>
        <h2>Tax handling</h2>
        <ul>
          <li>GST 28% on contest entry-fee equivalent (collected inclusive of deposits).</li>
          <li>TDS 30% on net winnings at the time of withdrawal (Sec 194BA).</li>
        </ul>
        <h2>Responsible gaming</h2>
        <ul>
          <li>Self-exclusion (temporary or permanent).</li>
          <li>Daily / weekly / monthly deposit limits.</li>
          <li>Daily session-time limit and reality-check intervals.</li>
        </ul>
        <h2>What we never do</h2>
        <ul>
          <li>No real-money cash-out from casino coins.</li>
          <li>No betting on third-party events.</li>
          <li>No credit / loans to play.</li>
          <li>No service to under-18 users.</li>
        </ul>
      </main>
    </>
  );
}
