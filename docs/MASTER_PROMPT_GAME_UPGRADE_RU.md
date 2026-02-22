# Master Prompt: апгрейд Neon Gridiron ULTRA (визуал + интерфейс + AI-мозг + обучение)

Ниже — большой production-ready промт для AI-агента (Codex/Claude/GPT), который должен сделать системный апгрейд проекта как полноценной 7v7 футбольной игры-симулятора с умным ИИ и качественной трансляцией матча.

---

## Готовый промт (копируй как есть)

```text
Ты Principal Engineer (Python + RL + Game AI + UI/UX + Systems Design).

Твоя задача: провести глубокую модернизацию проекта Neon Gridiron ULTRA как исследовательской 7v7 football платформы. Нужно многократно улучшить:
1) визуал и cinematic-подачу,
2) live-интерфейс и UX,
3) “мозг” ИИ (тактика, командная игра, принятие решений),
4) качество обучения (sample efficiency, стабильность, сила игры, разнообразие стратегий),
5) метрики и воспроизводимость.

Работай как lead-команда из нескольких треков: Gameplay, RL, Infra, Frontend, Telemetry.

========================================
0. Контекст проекта (используй как исходные ограничения)
========================================
- Это deterministic 7v7 платформа с Gymnasium env и observation shape (64,), action shape (28,).
- Есть live telemetry server (FastAPI/WebSocket + UDP ingest) и web UI (Next.js + canvas), плюс Godot-клиент.
- Сейчас env выглядит упрощённым и слишком “плоским” для реалистичной тактики: базовая кинематика, простой reward, упрощённая логика гола.
- PBT/Dreamer/curiosity присутствуют как scaffold, но требуют усиления для реального качества игры.

Нельзя ломать базовый API без адаптера обратной совместимости:
- Gym reset/step контракт,
- deterministic seed-reset,
- совместимость telemetry формата для UI.

========================================
1. Жёсткие критерии результата
========================================
После изменений должны выполняться:
A) Quality gates
- python -m ruff check .  -> 0 ошибок
- python -m ruff format --check . -> 0 ошибок
- python -m pytest -q -> все тесты зелёные

B) Functional goals
- Environment остаётся детерминированным при одинаковом seed
- Live UI запускается и показывает матч без падений импортов
- Telemetry единообразна (один canonical путь ingest->hub->ws)

C) AI goals (минимум)
- Агенты демонстрируют осмысленное движение без мяча (поиск пространства)
- В атаке видны хотя бы базовые паттерны: продвижение, пас, удар
- В обороне: возврат, давление на мяч, перекрытие зоны
- Средний xG и частота опасных моментов растут относительно baseline

D) Output goals
- Подготовь отчёт: что и зачем изменено, какие компромиссы, что дальше
- Приложи таблицу до/после по метрикам качества игры и обучения

========================================
2. План реализации (обязательный порядок)
========================================
Выполняй по фазам. После каждой фазы — тесты и короткий changelog.

ФАЗА 1 — Environment realism & state representation
1.1 Обнови model state:
- Добавь понятия ролей (GK/DEF/MID/FWD) и role-aware стартовые позиции 7v7.
- Расширь матчевые сигналы: владение, pressure index, progression lanes, опасные зоны.
- Сохрани итоговый observation как вектор фиксированной длины (обратная совместимость), но сделай feature packing структурированным (блоки ball/team/opponents/context).

1.2 Улучши физику и ball interaction:
- Более реалистичная инерция/затухание, ограничение ускорений, скоростной кап.
- Касание мяча с направлением, сила удара, перехваты, рикошеты.
- Простая модель усталости/стамины, влияющая на спринт и отбор.

1.3 Rules & events:
- Детализируй event stream: PASS, SHOT, TACKLE, INTERCEPTION, TURNOVER, PRESSURE_WIN, FINAL_THIRD_ENTRY.
- Убедись, что события детерминированы и пригодны для reward + explainability.

ФАЗА 2 — Reward redesign (многоуровневый, не хрупкий)
2.1 Раздели reward на компоненты:
- Sparse: goal scored/conceded.
- Dense offense: продвижение мяча, вход в последнюю треть, качество удара (xG proxy), успешные передачи вперёд.
- Dense defense: снижение xG соперника, перехваты, остановка прогрессии.
- Team coherence: spacing, поддержка игрока с мячом, компактность обороны.
- Discipline: штрафы за хаос/бесполезный дриблинг/потерю без давления.

2.2 Сделай configurable reward sets через yaml/json:
- baseline, attacking, defensive, balanced.
- Добавь auto-normalization/clip, чтобы reward scale не взрывался.

2.3 Валидация rewards:
- Unit tests для каждой компоненты.
- Интеграционный тест: при контролируемом сценарии reward знаки и порядок величин ожидаемы.

ФАЗА 3 — Policy architecture (мозг ИИ)
3.1 Перейди к multi-agent aware policy:
- Shared backbone + role heads или centralized critic / decentralized actors.
- Attention/transformer блок для взаимодействий “игрок-игрок-мяч”.
- Явная обработка контекста владения и фаз игры.

3.2 Hierarchical decision making:
- High-level option policy (режимы: build-up, counter, press, block).
- Low-level motor policy (конкретные действия).
- Переключение опций не каждый тик, а на макро-горизонте.

3.3 Tactical priors:
- Введи action masking / soft constraints по роли и контексту.
- Добавь heuristics teacher (небольшой scripted coach) для раннего bootstrapping.

ФАЗА 4 — Training stack overhaul
4.1 Curriculum learning:
- Stage 1: micro-skills (удар/пас/позиционирование).
- Stage 2: small-sided games (3v3/5v5) + доменные задачи.
- Stage 3: full 7v7 self-play.

4.2 Self-play + League:
- Elo-based matchmaking c anti-collapse мерами.
- Reservoir оппонентов (исторические снапшоты).
- Минимум 3 пула: exploiters, main, league evaluators.

4.3 Algorithmic upgrades:
- PPO+GAE как baseline, IMPALA/APPO как опция.
- Dreamer использовать только если world model стабилен по loss/rollout metrics.
- Curiosity ввести дозированно (коэффициенты по фазам curriculum).

4.4 Stability:
- Gradient clipping, entropy schedule, KL control, LR schedule, advantage normalization.
- Детальный logging: policy loss, value loss, entropy, explained variance, winrate vs checkpoints.

ФАЗА 5 — Tactical intelligence & explainability
5.1 Decision introspection:
- Для ключевых действий логируй reason codes (почему пас/удар/пресс).
- Сопоставляй outcome с ожидаемым value gain.

5.2 Team tactics metrics:
- Pass network centrality, pressing efficiency, transition speed, defensive compactness.
- Автоматические tactical reports по матчу.

5.3 Anti-degenerate checks:
- Датчики “карусельного” владения без прогрессии.
- Штраф за злоупотребление одной эксплойт-стратегией.

ФАЗА 6 — UI/UX & visual quality
6.1 Live UI overhaul:
- Красивый scoreboard, таймер, xG, владение, momentum bar, pressing intensity.
- Переключение камер: tactical top-down / broadcast / player focus.
- Speed control (0.5x/1x/2x) и replay последних N секунд.

6.2 Field rendering:
- Улучши canvas/webgl визуал: тени, motion trails, heatmap слои, pass arrows.
- Цветовые схемы команд + доступность (contrast-safe palette).

6.3 Analyst overlays:
- Оверлеи: линии паса, зоны давления, свободные коридоры, expected threat map.
- Вкл/выкл через UI toggles без перезагрузки.

ФАЗА 7 — Telemetry & backend coherence
7.1 Один canonical ingest pipeline:
- Удали/деактивируй дублирующий путь, оставь единый протокол.
- Версионируй frame schema (v2.x), добавь backward-compatible normalizer.

7.2 Performance:
- Batch/buffer отправки, контроль частоты кадров, graceful degradation.
- Добавь метрики latency/jitter/drop rate.

ФАЗА 8 — Eval harness & benchmarks
8.1 Match evaluation suite:
- 100+ матчей на фиксированных seed-пулаx.
- Таблица: winrate, xG for/against, goals, possession value, tactical diversity index.

8.2 Regression guardrails:
- Golden-seed replays: изменения не должны ломать детерминизм.
- Quality threshold gates для CI (минимум по метрикам).

========================================
3. Ограничения и принципы разработки
========================================
- Не оборачивай imports в try/catch.
- Сначала делай минимально инвазивные изменения с тестами, потом рефактор.
- Любой новый формат данных — через адаптер/normalizer.
- Каждую нетривиальную гипотезу подтверждай метриками, а не “кажется лучше”.
- Избегай massive rewrite без промежуточного working state.

========================================
4. Формат результата от тебя (обязательный)
========================================
Верни отчёт в структуре:
1) Executive Summary (10-15 буллетов)
2) Изменения по файлам (таблица: файл / что изменено / зачем / риск)
3) Обучение: конфиги, алгоритмы, schedules
4) Метрики до/после (таблица)
5) Демо-сценарий: как запустить live матч и увидеть улучшения
6) Какие ограничения остались
7) Next 30/60/90 day roadmap

И отдельно:
- Список выполненных команд с результатами
- Какие тесты добавлены
- Где потенциальный технический долг после изменений

========================================
5. Команды проверки, которые ты обязан выполнить
========================================
- python -m ruff format --check .
- python -m ruff check .
- python -m pytest -q
- (если доступно) UI build: npm ci && npm run build
- (если доступно) smoke live pipeline: запуск сервера + отправка тестового telemetry frame + проверка websocket клиента

========================================
6. Definition of Done
========================================
Считать задачу выполненной только если:
- Все quality gates зелёные
- Env детерминирован и тесты это подтверждают
- UI показывает расширенные live-метрики
- AI демонстрирует осмысленные тактические паттерны в 7v7
- Есть воспроизводимый отчёт по метрикам до/после
```

---

## Рекомендация по использованию

1. Вставь этот промт в новый диалог с агентом.
2. Добавь ограничение: “не делать гигантский PR, разбить на фазы 1→8 в отдельных PR”.
3. Попроси после каждой фазы показывать метрики и короткое видео/скрин live UI.
