# Промпт для чата-релизера скилла

Копируй этот текст в чат где обычно катишь новые версии скилла. Дай ему доступ к двум папкам:
- `~/Dev/BrickLink Studio Skill/` (сам скилл)
- `~/Dev/BrickitStudio/` (проект с рецептами и пакетиками)

---

## Промпт:

Нужно выпустить обновление скилла bricklink-studio до версии 1.6.0. Тема: полное покрытие Pockets — два рецепта генерации, колоринг, production pipeline.

Все материалы собраны в `~/Dev/BrickLink Studio Skill/updates/v1-6-0/`:

- `SKILL_UPDATE_BRIEF.md` — главный документ: что знаем, что было собрано, структура пробелов
- `source_*.md` — исходные данные: POCKETS.md, FAILED_APPROACHES.md, NOTES всех пакетиков, описания рецептов, session logs
- `contribution_*.md` — дополнения собранные из других чатов (эволюция алгоритмов, что не сработало, паттерны)

Рабочие скрипты и рецепты живут в `~/Dev/BrickitStudio/`:
- `Pockets-recipe-1/` — Gaussian rejection sampling pipeline (generator + fill_gaps + settle_y + packager)
- `Pockets-recipe-2/` — Sequential outward placement (generator + rotation_shuffle + fill_small_parts)
- `Pockets-coloring/` — 11 цветовых палеток + modifier_colorize + batch_colorize
- `Pockets/` — испытательный полигон, не трогать

Что нужно сделать:

1. Прочитай `SKILL_UPDATE_BRIEF.md` и все `source_*.md` / `contribution_*.md` файлы
2. Прочитай текущее состояние скилла: `SKILL.md`, `projects/part-piles/guide.md`, `learning/patterns.md`, `learning/failed.md`
3. Обнови скилл:

   **projects/part-piles/guide.md** — полный рерайт:
   - Два рецепта с описанием алгоритмов, параметров, пайплайнов
   - Таблица всех пакетиков P1–P19 с результатами
   - Колоринг-система (палетки, модификатор, batch)
   - Production pipeline (batch_generate, batch_colorize)
   - Размеры Small / Medium
   - .io packaging с правильным именованием моделей (0 Name: заголовок)

   **projects/part-piles/patterns.md** — подтвержденные паттерны из обоих рецептов

   **projects/part-piles/failed.md** — все провалы из обоих рецептов (объединить FAILED_APPROACHES.md + contribution файлы)

   **learning/patterns.md** — добавить общие паттерны (tilt_strength для flat piles, 6-8% floor для rejection sampling, и т.д.)

   **learning/failed.md** — добавить общие anti-patterns

4. Обнови CHANGELOG — версия 1.6.0, дата сегодня
5. Собери и запакуй скилл (`./build.sh`)
6. Покажи итоговый diff
