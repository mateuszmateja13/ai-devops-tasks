/**
 * Zwraca wszystkie pary elementów (różne indeksy), których suma równa się targetSum.
 * Wynik zawiera ten sam zbiór par co oryginalne findPairs; może się różnić tylko kolejność par.
 *
 * Złożoność: czas O(n + k), pamięć O(n) + wynik, gdzie k – liczba znalezionych par.
 *
 * @param {number[]} arr - tablica liczb
 * @param {number} targetSum - szukana suma
 * @returns {Array<[number, number]>} pary [wcześniejszy element, późniejszy element]
 */
function findPairsOptimized(arr, targetSum) {
  const pairs = [];
  const seen = new Map(); // wartość -> ile razy wystąpiła przed bieżącym elementem

  for (const value of arr) {
    const complement = targetSum - value;
    // Każde wcześniejsze wystąpienie dopełnienia tworzy jedną parę z bieżącym elementem
    const count = seen.get(complement) ?? 0;
    for (let k = 0; k < count; k++) {
      pairs.push([complement, value]);
    }
    seen.set(value, (seen.get(value) ?? 0) + 1);
  }
  return pairs;
}

/**
 * Zwraca unikalne pary wartości [a, b] (a <= b), których suma równa się targetSum.
 * Np. dla [3, 3, 3] i sumy 6 zwraca jedną parę [3, 3] zamiast trzech.
 *
 * Złożoność: czas O(n), pamięć O(n).
 *
 * @param {number[]} arr - tablica liczb
 * @param {number} targetSum - szukana suma
 * @returns {Array<[number, number]>} unikalne pary wartości
 */
function findUniquePairs(arr, targetSum) {
  const seen = new Set();
  const found = new Map(); // klucz "a,b" chroni przed duplikatami par

  for (const value of arr) {
    const complement = targetSum - value;
    if (seen.has(complement)) {
      const a = Math.min(value, complement);
      const b = Math.max(value, complement);
      found.set(`${a},${b}`, [a, b]);
    }
    seen.add(value);
  }
  return [...found.values()];
}

module.exports = { findPairsOptimized, findUniquePairs };
