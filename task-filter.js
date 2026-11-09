/**
 * Zwraca tytuły ukończonych zadań, posortowane rosnąco według id.
 *
 * @param {Array<{id: number, title: string, status: string}>} tasks - lista zadań
 * @returns {string[]} tytuły zadań o statusie "completed"
 */
function getCompletedTaskTitles(tasks) {
  if (!Array.isArray(tasks)) {
    throw new TypeError('Argument tasks musi być tablicą');
  }

  return tasks
    .filter((task) => task.status === 'completed') // tylko ukończone (filter tworzy kopię, oryginał bez zmian)
    .sort((a, b) => a.id - b.id)                    // rosnąco po id (porównanie liczbowe)
    .map((task) => task.title);                     // same tytuły
}

module.exports = { getCompletedTaskTitles };
