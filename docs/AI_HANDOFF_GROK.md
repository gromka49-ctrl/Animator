# AI handoff: Animator

Этот файл можно передать Grok, ChatGPT, Claude или локальному ИИ-кодеру вместе со ссылкой на репозиторий.

## Контекст

`Animator` — локальный редактор 3D-моделей и нейтральных анимаций персонажей. Основной стек: React 19, TypeScript, Vite, Three.js, React Three Fiber, Zustand и Tauri 2.

Проект уже умеет импортировать GLB, glTF, FBX и OBJ, показывать скелет, проигрывать встроенные клипы, редактировать позы, ставить keyframes, работать с timeline и экспортировать GLB.

## Правила работы ИИ

1. Сначала прочитай `README.md`, `src/types/model.ts`, `src/lib/clip-builder.ts`, `src/lib/rcanim-format.ts` и относящиеся к задаче компоненты.
2. Не переписывай приложение целиком и не объединяй код в один файл.
3. Перед изменением создай отдельную ветку или копию.
4. Не удаляй пользовательские исходники и не перезаписывай исходные модели.
5. После изменений запускай `npm run build` и `npm run lint`.
6. Для Blender используй GLB/glTF и формат `animation.json` из `examples/animation_clip.json`.
7. Если работаешь с телефоном, предпочитай браузерный режим и маленькие атомарные коммиты; не требуй локального Rust/Android SDK для обычной проверки интерфейса.

## Приоритет разработки

### Этап 1 — безопасный vertical slice

- импорт GLB в браузере;
- отображение модели и костей;
- timeline;
- добавление и перемещение keyframes;
- сохранение/загрузка `animation.json`;
- экспорт GLB.

### Этап 2 — Blender bridge

- импорт `animation.json` в Blender Action;
- экспорт выбранного Action обратно в JSON;
- отчёт об отсутствующих костях;
- тестовый файл из `examples/`.

### Этап 3 — качество анимации

- IK для рук/ног;
- joint limits;
- foot pinning;
- сглаживание и удаление выбросов;
- collision-debug для нейтральных объектов и прокси-коллайдеров.

## Как отвечать пользователю

Показывай изменённые файлы, команды проверки и ограничения. Не заявляй, что FBX или Blender поддерживаются, если это не проверено конкретным тестом. Предпочитай переносимые форматы GLB, glTF, BVH и JSON.

## Команды

```bash
npm install
npm run dev:web
npm run build
npm run lint
```

Для Blender:

```text
Blender → Edit → Preferences → Add-ons → Install…
выбрать blender_addon/animator_bridge.py
```
