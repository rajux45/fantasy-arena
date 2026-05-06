import { Nav } from '@/components/Nav';

const RULES = {
  cricket: {
    icon: '🏏',
    sections: [
      { title: 'Batting', items: ['Run = +1', 'Boundary bonus = +1', 'Six bonus = +2', 'Half-century = +8', 'Century = +16', 'Duck (not bowler) = −2'] },
      { title: 'Bowling', items: ['Wicket = +25', '4-wicket haul = +8', '5-wicket haul = +16', 'Maiden over (T20) = +12'] },
      { title: 'Fielding', items: ['Catch = +8', '3 catches = +4', 'Stumping = +12', 'Run-out (direct) = +12', 'Run-out (assist) = +6'] },
      { title: 'Captain & Vice-captain', items: ['Captain = 2× points', 'Vice-captain = 1.5× points'] },
    ],
  },
  football: {
    icon: '⚽',
    sections: [
      { title: 'Playing time', items: ['Played 60+ min = +2', 'Played < 60 min = +1'] },
      { title: 'Goals (by position)', items: ['GK = +12', 'DEF = +10', 'MID = +8', 'FWD = +6'] },
      { title: 'Other', items: ['Assist = +6', 'Clean sheet (GK/DEF) = +4', 'Yellow card = −1', 'Red card = −3', 'Penalty save (GK) = +12'] },
    ],
  },
  kabaddi: {
    icon: '🤼',
    sections: [
      { title: 'Raid', items: ['Raid point = +3', 'Bonus point = +1', 'Touch (multiple defenders) = +1 each'] },
      { title: 'Defense', items: ['Tackle = +2', 'Super tackle = +4'] },
      { title: 'Bonuses', items: ['Super 10 (10 raid pts) = +6', 'High 5 (5 tackles) = +6'] },
    ],
  },
  basketball: {
    icon: '🏀',
    sections: [
      { title: 'Stats', items: ['Point = +1', '3-pointer bonus = +1', 'Rebound = +1.2', 'Assist = +1.5', 'Steal = +2', 'Block = +2'] },
      { title: 'Penalties', items: ['Turnover = −1', 'Missed shot = −0.5'] },
      { title: 'Bonuses', items: ['Double-double = +6', 'Triple-double = +12'] },
    ],
  },
};

export default function ScoringRulesPage() {
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Scoring rules</h1>
        <p className="mt-1 text-sm text-slate-400">Pure skill: the player you pick scores fantasy points based on their real-game performance.</p>
        <div className="mt-6 grid gap-6 md:grid-cols-2">
          {Object.entries(RULES).map(([sport, cfg]) => (
            <section key={sport} className="card">
              <h2 className="text-xl font-semibold capitalize">{cfg.icon} {sport}</h2>
              {cfg.sections.map((sec) => (
                <div key={sec.title} className="mt-3">
                  <h3 className="text-sm font-medium text-slate-300">{sec.title}</h3>
                  <ul className="mt-1 space-y-0.5 text-sm text-slate-400">
                    {sec.items.map((it) => <li key={it}>· {it}</li>)}
                  </ul>
                </div>
              ))}
            </section>
          ))}
        </div>
      </main>
    </>
  );
}
