# Blender bridge

`blender_addon/animator_bridge.py` — небольшой аддон без внешних зависимостей.

## Установка

1. Открыть Blender.
2. Перейти в `Edit → Preferences → Add-ons → Install…`.
3. Выбрать `blender_addon/animator_bridge.py`.
4. Включить аддон.

## Импорт

1. Выбрать Armature в сцене.
2. `File → Import → Animator JSON Clip`.
3. Выбрать `examples/animation_clip.json`.
4. Аддон создаст Action и вставит keyframes на найденные кости.

## Экспорт

1. Выбрать Armature с активным Action.
2. `File → Export → Animator JSON Clip`.
3. Полученный JSON можно передать в Animator или другому ИИ.

## Ограничения

- имена костей должны совпадать;
- Quaternion хранится как `[x, y, z, w]`;
- FBX не используется как промежуточный формат;
- для сложного retargeting нужен отдельный профиль соответствий;
- аддон работает с обычными костями и keyframes, без специализированного контента.
