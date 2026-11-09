// Oryginalna wersja funkcji zwracającej konfigurację środowiska
function getEnvironmentConfig(env) {
  if (env === 'development') {
    return {
      apiUrl: 'http://localhost:3000/api',
      debug: true,
      timeout: 5000
    };
  } else if (env === 'testing') {
    return {
      apiUrl: 'http://test-server:3000/api',
      debug: true,
      timeout: 5000
    };
  } else if (env === 'staging') {
    return {
      apiUrl: 'https://staging.example.com/api',
      debug: false,
      timeout: 10000
    };
  } else if (env === 'production') {
    return {
      apiUrl: 'https://api.example.com',
      debug: false,
      timeout: 15000
    };
  } else {
    return {
      apiUrl: 'http://localhost:3000/api',
      debug: true,
      timeout: 5000
    };
  }
}

module.exports = { getEnvironmentConfig };
