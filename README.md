Загрузка всех вакансий за последний месяц:

```bash
# загрузка вакансий
./load.bash
# удаление возможных дубликатов
cat vacancies | sort -u > vacancies.unique
```

Топ зарплат и количества по городам всех вакансий:

```bash
# анализ вакансий
cat vacancies.unique | ./analyze.py --data_1 profareas --data_2 areas -s salary.average
# преобразование топа зарплат из CSV в Markdown
cat profareas.salary.average.csv | head -n 11 | csvtomd - > profareas.salary.average.md
# преобразование топа городов из CSV в Markdown
cat areas.csv | head -n 11 | csvtomd - > areas.md
# построение графика по топу зарплат
./chart.py -c1 -l10 -yRUB profareas.salary.average.csv
# построение графика по топу городов
./chart.py -c1 -l10 -yВакансий areas.csv
```

Топ зарплат вакансий с инвалидностью:

```bash
# анализ вакансий
cat vacancies.unique | ./analyze.py --data_1 profareas -s salary.average -H
# преобразование топа зарплат из CSV в Markdown
cat profareas.salary.average.handicapped.csv | head -n 11 | csvtomd - > profareas.salary.average.handicapped.md
# построение графика по топу зарплат
./chart.py -c1 -l10 -yRUB profareas.salary.average.handicapped.csv
```

Топ зарплат вакансий с удалённой работой:

```bash
# анализ вакансий
cat vacancies.unique | ./analyze.py --data_1 profareas -s salary.average -r
# преобразование топа зарплат из CSV в Markdown
cat profareas.salary.average.remote.csv | head -n 11 | csvtomd - > profareas.salary.average.remote.md
# построение графика по топу зарплат
./chart.py -c1 -l10 -yRUB profareas.salary.average.remote.csv
```

Топ зарплат вакансий без опыта работы:

```bash
# анализ вакансий
cat vacancies.unique | ./analyze.py --data_1 profareas -s salary.average -e
# преобразование топа зарплат из CSV в Markdown
cat profareas.salary.average.no_experience.csv | head -n 11 | csvtomd - > profareas.salary.average.no_experience.md
# построение графика по топу зарплат
./chart.py -c1 -l10 -yRUB profareas.salary.average.no_experience.csv
```

Топ зарплат вакансий уборщицы:

```bash
# анализ вакансий
cat vacancies.unique | ./analyze.py --data_1 profareas -s salary.average -qуборщ
# преобразование топа зарплат из CSV в Markdown
cat profareas.salary.average.уборщ.csv | head -n 11 | csvtomd - > profareas.salary.average.уборщ.md
# построение графика по топу зарплат
./chart.py -c1 -l10 -yRUB profareas.salary.average.уборщ.csv
```
