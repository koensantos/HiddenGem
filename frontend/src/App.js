import React, { useState } from 'react';

function App() {
  const [rawData, setRawData] = useState(null);
  const [error, setError] = useState(null);
  const [song, setSong] = useState('Blinding Lights');
  const [minMonthlyListeners, setMinMonthlyListeners] = useState('1000');
  const [maxMonthlyListeners, setMaxMonthlyListeners] = useState('50000000');
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setRawData(null);
    setIsLoading(true);

    // Keep the payload aligned with validate_recommendation_request in the Flask API.
    try {
      const response = await fetch('/recommendations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        song_name: song,
        min_monthly_listeners: Number(minMonthlyListeners),
        max_monthly_listeners: Number(maxMonthlyListeners),
      }),
    });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Request failed.');
      setRawData(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="panel">
        <p className="eyebrow">Hidden Gem</p>
        <h1>Find songs by reach</h1>
        <p className="intro">Enter a song and listener range to get recommendations from the API.</p>

        <form onSubmit={handleSubmit}>
          <label>
            Song
            <input value={song} onChange={(event) => setSong(event.target.value)} required minLength={3} />
          </label>
          <div className="range-fields">
            <label>
              Minimum monthly listeners
              <input type="number" min="0" value={minMonthlyListeners} onChange={(event) => setMinMonthlyListeners(event.target.value)} required />
            </label>
            <label>
              Maximum monthly listeners
              <input type="number" min="0" value={maxMonthlyListeners} onChange={(event) => setMaxMonthlyListeners(event.target.value)} required />
            </label>
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Get recommendations'}
          </button>
        </form>

        {error && <p className="error">{error}</p>}
        {/* Keep this unfiltered so new fields added by the API are visible automatically. */}
        {rawData && (
          <div className="response">
            <h2>Raw JSON response</h2>
            <pre>{JSON.stringify(rawData, null, 2)}</pre>
          </div>
        )}
      </section>
    </main>
  );
}

export default App;
