# Тестовые входы

| Файл | Что это |
| :--- | :--- |
| `requirements.docx` | `docs/requirements.md`, сконвертированный pandoc |
| `requirements.pdf` | тот же DOCX, экспорт в PDF через LibreOffice (текст разбит на фрагменты — проверка чтения PDF) |
| `password-reset.md` | второй, «чужой» документ другой предметной области — проверка, что агент не подогнан под один файл |

Пересобрать DOCX и PDF:

```bash
pandoc docs/requirements.md -o samples/requirements.docx
soffice --headless --convert-to pdf --outdir samples samples/requirements.docx
```
