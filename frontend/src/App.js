import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

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
      if (typeof data == 'undefined'){
        throw new Error("Data not initialized.")
      }
      if (typeof data.recommendations == 'undefined'){
        throw new Error("JSON is erroneous")
      }
      if (!Array.isArray(data.recommendations)){
        throw new Error("Wrong object.")
      }
      setRawData(data.recommendations);
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

        <div className="d-flex justify-content-center align-items-center min-vh-100">
          <form onSubmit={handleSubmit} className='w-100' style={{ maxWidth: '400px' }}>
            <label className="mb-3 d-flex flex-column">
              Song
              <input value={song} onChange={(event) => setSong(event.target.value)} required minLength={3} />
            </label>
            <div className="range-fields">
              <label className="mb-3 d-flex flex-column">
                Minimum monthly listeners
                <input type="number" min="0" value={minMonthlyListeners} onChange={(event) => setMinMonthlyListeners(event.target.value)} required />
              </label>
              <label className="mb-3 d-flex flex-column">
                Maximum monthly listeners
                <input type="number" min="0" value={maxMonthlyListeners} onChange={(event) => setMaxMonthlyListeners(event.target.value)} required />
              </label>
            </div>
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Loading...' : 'Get recommendations'}
            </button>
          </form>
        </div>

        {error && <p className="error">{error}</p>}
        {/* Keep this unfiltered so new fields added by the API are visible automatically. */}
        <div className="row g-4 mb-5">
          {Array.isArray(rawData) ? (
            rawData.map((item, index) => (
              /* Cards take up 12 cols on mobile, 6 on tablet, 4 on desktop */
              <div className="col-12 col-md-6 col-lg-4" key={item.id || index}>
                <div className="card h-100 shadow-sm border-start border-4 border-primary">
                  <div className="card-body">
                    {Object.entries(item).map(([key, value]) => (
                      <div className="mb-3" key={key}>
                        <small className="text-muted fw-bold text-uppercase d-block mb-1">
                          {key.replace(/([A-Z])/g, ' $1')}
                        </small>
                        <p className="card-text text-dark word-break">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))
          ) : rawData ? (
            /* Fallback for a single JSON object instead of an array */
            <div className="col-12 col-md-8 col-lg-6 mx-auto">
              <div className="card shadow-sm border-start border-4 border-primary">
                <div className="card-body">
                  {Object.entries(rawData).map(([key, value]) => (
                    <div className="mb-3" key={key}>
                      <small className="text-muted fw-bold text-uppercase d-block mb-1">
                        {key.replace(/([A-Z])/g, ' $1')}
                      </small>
                      <p className="card-text text-dark">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </section>
    </main>
  );
}

export default App;
