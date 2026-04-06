# Промпт для чатов-источников знаний

Копируй этот текст в каждый чат который работал над Pockets. Не забудь дать чату доступ к папке `~/Dev/BrickLink Studio Skill/updates/v1-6-0/`.

---

## Промпт:

Мы обновляем скилл bricklink-studio — нужно собрать все знания о генерации Pockets из этого чата.

Прочитай файл `~/Dev/BrickLink Studio Skill/updates/v1-6-0/SKILL_UPDATE_BRIEF.md` — там описано что мы уже знаем и какие пробелы нужно заполнить.

Твоя задача:

1. Прочитай SKILL_UPDATE_BRIEF.md целиком
2. Определи какие пробелы из секции "2. What's Missing" относятся к работе в этом чате
3. Создай файл `~/Dev/BrickLink Studio Skill/updates/v1-6-0/contribution_{topic}.md` где {topic} — краткое описание того что ты добавляешь (например `contribution_p12-sequential-algorithm.md` или `contribution_coloring-palettes.md`)
4. В файле опиши на английском:
   - What was developed in this chat (which Pockets, which algorithms)
   - Evolution: version by version, what changed, what problem each version solved
   - What failed: specific approaches tried and abandoned, with WHY
   - Confirmed patterns: things that reliably work and should be reused
   - Parameters tuned: before/after values, how final values were determined
   - Scripts created: what each does, where it lives
   - Open questions or next steps discussed but not implemented

Пиши подробно — лучше больше деталей чем меньше. Это пойдет в скилл который будет использоваться в будущих сессиях.

Не трогай другие файлы в этой папке. Только создай свой contribution_ файл.
