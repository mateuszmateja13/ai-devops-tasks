/**
 * Walidacja formatu adresu IPv4 za pomocą wyrażenia regularnego.
 *
 * Oktet: 25[0-5] (250–255) | 2[0-4][0-9] (200–249) | 1[0-9]{2} (100–199) | [1-9]?[0-9] (0–99)
 * Zera wiodące (np. "01") są odrzucane, bo część systemów traktuje je jako zapis ósemkowy.
 */
const IPV4_REGEX =
  /^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$/;

/**
 * Sprawdza, czy podana wartość jest poprawnym adresem IPv4 w notacji kropkowej.
 *
 * @param {unknown} address - wartość do sprawdzenia
 * @returns {boolean} true, jeśli wartość jest poprawnym adresem IPv4
 */
function isValidIPv4(address) {
  // Wartości niebędące tekstem odrzucamy od razu, zamiast niejawnie konwertować je na string
  if (typeof address !== 'string') {
    return false;
  }
  return IPV4_REGEX.test(address);
}

module.exports = { isValidIPv4, IPV4_REGEX };

// Demonstracja i testy po uruchomieniu bezpośrednio: node ipv4-validator.js
if (require.main === module) {
  const valid = ['192.168.1.1', '10.0.0.1', '172.16.254.99', '0.0.0.0', '255.255.255.255', '8.8.8.8'];
  const invalid = [
    '256.1.1.1', '999.999.999.999', '192.168.1', '192.168.1.1.1', '192.168.01.1',
    '1..2.3', 'a.b.c.d', '192.168.1.-1', ' 192.168.1.1', '192.168.1.1/24', '',
    null, undefined, 19216811,
  ];

  let failures = 0;
  for (const ip of valid) {
    const ok = isValidIPv4(ip);
    console.log(`${ok ? '✅' : '❌'} ${JSON.stringify(ip).padEnd(20)} oczekiwano: true,  wynik: ${ok}`);
    if (!ok) failures++;
  }
  for (const ip of invalid) {
    const ok = isValidIPv4(ip);
    console.log(`${!ok ? '✅' : '❌'} ${String(JSON.stringify(ip)).padEnd(20)} oczekiwano: false, wynik: ${ok}`);
    if (ok) failures++;
  }

  const total = valid.length + invalid.length;
  console.log(failures === 0
    ? `\nOK – wszystkie ${total} przypadków zgodne z oczekiwaniami`
    : `\nNiepowodzenia: ${failures} z ${total}`);
  process.exit(failures ? 1 : 0);
}
