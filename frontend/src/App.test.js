import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

describe('App', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
  });

  test('renders the recommendation form with default values', () => {
    render(<App />);

    expect(screen.getByText(/hidden gem/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /find songs by reach/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/song/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/minimum monthly listeners/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/maximum monthly listeners/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('Blinding Lights')).toBeInTheDocument();
    expect(screen.getByDisplayValue('1000')).toBeInTheDocument();
    expect(screen.getByDisplayValue('50000000')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /get recommendations/i })).toBeInTheDocument();
  });

  test('submits the selected values to the recommendations API and renders the response', async () => {
    const mockFetch = jest.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        recommendations: [{ song: 'Midnight City', artist: 'M83' }],
        count: 1,
      }),
    });

    const user = userEvent.setup();
    render(<App />);

    await user.clear(screen.getByLabelText(/song/i));
    await user.type(screen.getByLabelText(/song/i), 'Midnight City');
    await user.clear(screen.getByLabelText(/minimum monthly listeners/i));
    await user.type(screen.getByLabelText(/minimum monthly listeners/i), '25000');
    await user.clear(screen.getByLabelText(/maximum monthly listeners/i));
    await user.type(screen.getByLabelText(/maximum monthly listeners/i), '2000000');

    await user.click(screen.getByRole('button', { name: /get recommendations/i }));

    expect(mockFetch).toHaveBeenCalledWith(
      '/recommendations',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          song: 'Midnight City',
          min_monthly_listeners: 25000,
          max_monthly_listeners: 2000000,
        }),
      })
    );

    expect(await screen.findByText('Midnight City')).toBeInTheDocument();
    expect(screen.getByText('M83')).toBeInTheDocument();
  });

  test('shows an error message when the recommendations request fails', async () => {
    jest.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      json: async () => ({ error: 'No recommendations found for that range.' }),
    });

    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: /get recommendations/i }));

    expect(await screen.findByText('No recommendations found for that range.')).toBeInTheDocument();
    expect(screen.queryByText('Midnight City')).not.toBeInTheDocument();
  });

  test('shows a validation error without sending an invalid listener range', async () => {
    const mockFetch = jest.spyOn(global, 'fetch');
    const user = userEvent.setup();
    render(<App />);

    await user.clear(screen.getByLabelText(/minimum monthly listeners/i));
    await user.type(screen.getByLabelText(/minimum monthly listeners/i), '5000000');
    await user.clear(screen.getByLabelText(/maximum monthly listeners/i));
    await user.type(screen.getByLabelText(/maximum monthly listeners/i), '1000');
    await user.click(screen.getByRole('button', { name: /get recommendations/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Minimum monthly listeners must not exceed the maximum.'
    );
    expect(mockFetch).not.toHaveBeenCalled();
  });

  test('shows a loading state while the recommendations request is pending', async () => {
    let resolveFetch;
    jest.spyOn(global, 'fetch').mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveFetch = resolve;
        })
    );

    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: /get recommendations/i }));

    expect(screen.getByRole('button', { name: /loading.../i })).toBeDisabled();
    expect(screen.getByRole('status')).toHaveTextContent('Loading recommendations...');

    resolveFetch({
      ok: true,
      json: async () => ({ recommendations: [] }),
    });

    await waitFor(() =>
      expect(screen.getByRole('button', { name: /get recommendations/i })).toBeEnabled()
    );
  });
});
