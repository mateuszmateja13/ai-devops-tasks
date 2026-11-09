// sum.test.js – testy jednostkowe funkcji sum
const sum = require('./sum');

describe('sum', () => {
  test('dodaje dwie liczby dodatnie', () => {
    expect(sum(2, 3)).toBe(5);
  });

  test('obsługuje liczby ujemne', () => {
    expect(sum(-4, 1)).toBe(-3);
  });

  test('dodaje zero bez zmiany wyniku', () => {
    expect(sum(7, 0)).toBe(7);
  });

  test('dla ułamków porównuje wynik z tolerancją', () => {
    // 0.1 + 0.2 daje 0.30000000000000004, dlatego używamy toBeCloseTo
    expect(sum(0.1, 0.2)).toBeCloseTo(0.3);
  });
});
