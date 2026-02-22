# Почему «в GitHub ничего не поменялось»

Если вы смотрите страницу `Commits` для ветки `main`, а изменения были сделаны в другой ветке (`work`, `fix/...`), в `main` их не будет видно до merge.

## Самый простой путь (из корня репозитория)

```bat
publish_branch_to_main.cmd fix/baseline-restore
```

## Проверка

```bat
git branch -a
git log --oneline --decorate -n 15
```

## Альтернатива (через scripts/)

```bat
scripts\publish_branch_to_main.cmd fix/baseline-restore
```

## Без скриптов (всегда работает)

```bat
git fetch origin
git checkout main
git pull --ff-only origin main
git merge --no-ff fix/baseline-restore -m "Merge fix/baseline-restore into main"
git push origin main
```

## Если `scripts\*.cmd` «не найдены»

Значит локальный клон ещё не содержит эти файлы.
Сначала синхронизируйте репозиторий:

```bat
git fetch origin
git checkout main
git pull origin main
dir scripts
```

После этого используйте root-скрипт `publish_branch_to_main.cmd`.
