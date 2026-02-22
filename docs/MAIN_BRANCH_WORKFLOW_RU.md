# Работа только в одной ветке `main`

По вашему требованию дальнейшая работа ведётся только в `main`.

## Правила
- Не создавать feature-ветки (`work`, `fix/*`, `codex/*`).
- Все изменения делать и коммитить сразу в `main`.
- Публиковать напрямую в `origin/main`.

## Проверка
```bash
git rev-parse --abbrev-ref HEAD
```
Ожидаемый результат: `main`.

## Базовый цикл
```bash
git checkout main
git pull --ff-only origin main
# изменения
python -m ruff check .
python -m pytest -q
git add -A
git commit -m "<message>"
git push origin main
```

## Если сейчас не в main
```bash
git checkout main
```
