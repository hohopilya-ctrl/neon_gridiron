# Подтверждение коммита

Если кажется, что коммит “не добавился”, проверь локально:

```bash
git log --oneline -n 5
git status -sb
```

Актуальный коммит с глобальными улучшениями:

- `7cb5764` — `Implement broad 7v7 tactical env and training foundation upgrades`

Если в GitHub его не видно, обычно причина в том, что ветка не запушена в `origin`.

Проверить и отправить:

```bash
git remote -v
git branch -vv
git push -u origin work
```
