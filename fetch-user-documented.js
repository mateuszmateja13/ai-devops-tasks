/**
 * Dane użytkownika zwracane przez funkcję fetchUserData.
 * @typedef {Object} UserData
 * @property {string} name - Imię i nazwisko użytkownika.
 * @property {string} email - Adres e-mail użytkownika.
 * @property {Date|null} lastLogin - Data ostatniego logowania lub null, gdy API jej nie zwraca.
 */

/**
 * Pobiera dane użytkownika z API i zwraca je w uproszczonej postaci.
 *
 * @async
 * @param {string|number} userId - Identyfikator użytkownika. Jest kodowany przed wstawieniem do URL.
 * @returns {Promise<UserData|null>} Obiekt z danymi użytkownika albo null, gdy żądanie się nie powiedzie.
 *
 * @example
 * const user = await fetchUserData(42);
 * if (user) {
 *   console.log(user.name, user.lastLogin);
 * }
 */
async function fetchUserData(userId) {
  try {
    // Kodujemy identyfikator, aby uniknąć problemów ze znakami specjalnymi w URL
    const response = await fetch(`https://api.example.com/users/${encodeURIComponent(userId)}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Brak znacznika czasu daje null zamiast "Invalid Date"
    const lastLogin = data.lastLoginTimestamp != null
      ? new Date(data.lastLoginTimestamp)
      : null;

    return { name: data.name, email: data.email, lastLogin };
  } catch (error) {
    console.error('Fetch error:', error);
    return null;
  }
}
