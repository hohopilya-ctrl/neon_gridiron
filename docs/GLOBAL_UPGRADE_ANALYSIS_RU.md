# Глобальный анализ проекта и программа масштабного улучшения

## 1) Что уже хорошо
- Базовая структура по слоям (sim / ai / telemetry / ui / server) уже присутствует.
- Есть deterministic-поток для env и автотесты на повторяемость.
- Есть основа для live-трансляции через UDP -> WS.

## 2) Основные ограничения
- Среда слишком упрощена для “футбольного мышления” (тактика, позиционка, роли).
- Reward раньше фокусировался почти только на простых плотностях и голах.
- Отсутствовал tactical-layer для объяснимых решений (режимы игры, контекст).
- Curriculum был минимальным и не покрывал progression до full 7v7 качества.

## 3) Что улучшено в этом апдейте
- Углублена логика `NeonFootballEnv`: role-based старт, стамина, инерция, события прогрессии.
- RewardShaper расширен до иерархии компонент: goal/offense/defense/dense/spec.
- Добавлен tactical subsystem (`ai/tactics`) с formation planner и coach decision layer.
- Curriculum пересобран под staged growth (micro-skills -> small-sided -> full_7v7).

## 4) Почему это важно
- Это даёт более “осмысленную” динамику для self-play и улучшает signal quality для RL.
- Повышает шанс обучения комбинационным паттернам (продвижение, вход в финальную треть).
- Создаёт основу для explainability через tactical decisions/режимы.

## 5) Следующий шаг (roadmap)
1. Добавить offline evaluation-suite: xG diff, progression rate, pressure win rate.
2. Подключить tactical features в policy encoder (attention over teammates/opponents).
3. Визуально отрисовать tactical overlays в UI (corridors/pressing map/pass network).
4. Укрепить league/self-play c reservoir opponents и anti-collapse checks.
