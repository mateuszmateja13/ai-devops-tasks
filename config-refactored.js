// Zrefaktoryzowana wersja funkcji zwracającej konfigurację środowiska

// Wartości wspólne dla większości środowisk (domyślnie: lokalny development)
const BASE_CONFIG = Object.freeze({
  apiUrl: 'http://localhost:3000/api',
  debug: true,
  timeout: 5000,
});

// Każde środowisko definiuje wyłącznie różnice względem BASE_CONFIG
const ENV_OVERRIDES = Object.freeze({
  development: {},
  testing:    { apiUrl: 'http://test-server:3000/api' },
  staging:    { apiUrl: 'https://staging.example.com/api', debug: false, timeout: 10000 },
  production: { apiUrl: 'https://api.example.com',         debug: false, timeout: 15000 },
});

/**
 * Zwraca konfigurację dla wskazanego środowiska.
 * Nieznane lub puste środowisko otrzymuje konfigurację deweloperską (jak w oryginale).
 * @param {string} env - nazwa środowiska
 * @returns {{apiUrl: string, debug: boolean, timeout: number}}
 */
function getEnvironmentConfig(env) {
  // Object.hasOwn chroni przed kluczami z prototypu, np. 'toString'
  const overrides = Object.hasOwn(ENV_OVERRIDES, env)
    ? ENV_OVERRIDES[env]
    : ENV_OVERRIDES.development;
  // Nowy obiekt przy każdym wywołaniu, aby nie modyfikować współdzielonych stałych
  return { ...BASE_CONFIG, ...overrides };
}

module.exports = { getEnvironmentConfig };
