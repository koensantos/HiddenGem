import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import './App.css';

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

    const minimumListeners = Number(minMonthlyListeners);
    const maximumListeners = Number(maxMonthlyListeners);
    if (!Number.isFinite(minimumListeners) || !Number.isFinite(maximumListeners)) {
      setError('Listener counts must be valid numbers.');
      return;
    }
    if (minimumListeners > maximumListeners) {
      setError('Minimum monthly listeners must not exceed the maximum.');
      return;
    }

    setIsLoading(true);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      let response;
      try {
        response = await fetch('/recommendations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            song,
            min_monthly_listeners: minimumListeners,
            max_monthly_listeners: maximumListeners,
          }),
          signal: controller.signal
        });
      } catch (networkError) {
        clearTimeout(timeoutId);
        if (networkError.name === 'AbortError') {
          throw new Error('Backend request timed out after 10 seconds. Is the backend running?');
        }
        throw new Error(`Cannot reach backend: ${networkError.message}`);
      }

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = 'Request failed.';
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || `Backend error: ${response.status}`;
        } catch {
          errorMessage = `Backend error: ${response.status}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
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
        <header className="text-center intro-header">
          <h1>HiddenGem</h1>
          <h2>Find your niche music</h2>
          <p className="intro">Enter a song and listener range to get recommendations from the API.</p>
        </header>



        <div className="d-flex justify-content-center align-items-center min-vh-10">
          <form onSubmit={handleSubmit} className='w-100' style={{ maxWidth: '400px' }} aria-busy={isLoading}>
            {error && <p className="error" role="alert">{error}</p>}

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
            {isLoading && <p className="status" role="status" aria-live="polite">Loading recommendations...</p>}
          </form>
        </div>

        {/* Keep this unfiltered so new fields added by the API are visible automatically. */}
        <div className="row g-4 mb-5 min-vh-10 pt-4">
          {Array.isArray(rawData) ? (
            rawData.length > 0 ? (
              rawData.map((item, index) => {
                // Safety check: ensure item is a valid object
                if (!item || typeof item !== 'object') {
                  return null;
                }
                return (
                  /* Cards take up 12 cols on mobile, 6 on tablet, 4 on desktop */
                  <div className="col-12 col-md-6 col-lg-4" key={`${item.track_name || ''}-${index}`}>
                    <div className="card h-100 shadow-sm border-start border-4 border-primary">
                      <div className="card-body">
                        {Object.entries(item).map(([key, value]) => {
                          // Format values based on field type
                          let displayValue = value;
                          if (key === 'monthly_listeners' && typeof value === 'number') {
                            displayValue = value.toLocaleString();
                          } else if (key === 'cosine_similarity' && typeof value === 'number') {
                            displayValue = value.toFixed(4);
                          } else if (typeof value === 'object') {
                            displayValue = JSON.stringify(value);
                          } else {
                            displayValue = String(value);
                          }

                          // Format key: convert snake_case and camelCase to Title Case
                          const formattedKey = key
                            .replace(/_/g, ' ')
                            .replace(/([A-Z])/g, ' $1')
                            .trim()
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                            .join(' ');

                          return (
                            <div className="mb-3" key={key}>
                              <small className="text-muted fw-bold text-uppercase d-block mb-1">
                                {formattedKey}
                              </small>
                              <p className="card-text text-dark word-break">
                                {displayValue}
                              </p>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              /* No results case */
              <div className="col-12">
                <div className="alert alert-info" role="alert">
                  <strong>No recommendations found</strong> for "{song}" with {minMonthlyListeners} - {maxMonthlyListeners} monthly listeners. Try adjusting your search criteria.
                </div>
              </div>
            )
          ) : rawData ? (
            /* Fallback for a single JSON object instead of an array */
            <div className="col-12 col-md-8 col-lg-6 mx-auto">
              <div className="card shadow-sm border-start border-4 border-primary">
                <div className="card-body">
                  {Object.entries(rawData).map(([key, value]) => (
                    <div className="mb-3" key={key}>
                      <small className="text-muted fw-bold text-uppercase d-block mb-1">
                        {key.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
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
    </main>
  );
}

export default App;
