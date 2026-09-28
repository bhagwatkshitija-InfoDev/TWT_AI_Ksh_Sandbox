# Chinese Formatting Checklist

Apply every rule below to the document. Quote the exact offending text and its location.

## 1. Full-width vs half-width punctuation
Chinese prose uses full-width punctuation: ，。！？；： and full-width parentheses （）.
Do not use the half-width ASCII forms , . ! ? ; : ( ) for Chinese sentences.

- Incorrect: 你好,世界！这是一个测试.
- Correct: 你好，世界！这是一个测试。

Exception: punctuation inside inline code, URLs, file paths, or an embedded Latin-script
term stays half-width (e.g., `config.json`, `example.com`).

## 2. Spacing around mixed Chinese/Latin/number text
Insert one half-width space between CJK characters and adjacent Latin letters or digits.
Do not insert a space between CJK characters and adjacent full-width punctuation.

- Incorrect: 请安装Python3.11版本 / 价格是100元
- Correct: 请安装 Python 3.11 版本 / 价格是 100 元
- Incorrect (space before full-width punctuation): 你好 ，世界
- Correct: 你好，世界

## 3. Chinese quotation and title marks
Use 「」 (or nested 『』) for quotations, and 《》 for titles of books/articles/works.
Do not use Western " " or ' ' quotes for Chinese text.

- Incorrect: 他说"你好"。我读了《西游记》。
- Correct: 他说「你好」。我读了《西游记》。
- Nested quote example: 他说：「我读过『红楼梦』。」

## 4. Table formatting — Chinese characters must not be stacked one-per-line
Inside a table cell, Chinese text must render as one continuous line, never with each
character forced onto its own line/row within the cell.

How this bug shows up in the source:
- A line break, `<br>`/`<br/>`, or literal newline inserted between every individual
  Chinese character inside a cell.
- A fixed or narrow column width (e.g., `width="20"`, a narrow `ch`/pixel value) applied
  to a column that holds multi-character CJK content, which will force character-wrapping
  when rendered.
- In a plain Markdown table, literal padding spaces or newlines inserted between every
  character to force alignment.

Examples:
- Incorrect (HTML): `<td>产<br>品<br>名<br>称</td>`
- Incorrect (narrow fixed width forcing wrap): `<th style="width:20px">产品名称</th>`
  with multi-character content in that column
- Incorrect (Markdown padding): `| 产 品 名 称 |`
- Correct: `<td>产品名称</td>` / `| 产品名称 |` — no forced line breaks, no artificially
  narrow width, content reads as one line per cell.

---

## 5. Ellipsis and dash (additional)
Use the Chinese ellipsis "……" (two three-dot ideographic units, six dots total) and the
Chinese em dash pair "——", not the ASCII "..." or "--".

- Incorrect: 这样下去...会有问题--真的。
- Correct: 这样下去……会有问题——真的。

## 6. No doubled/redundant punctuation (additional)
Avoid stacking marks such as "。。", "！！！", "，，" for emphasis; use a single mark.

- Incorrect: 太好了！！！ 这样可以吗。。
- Correct: 太好了！这样可以吗。

## 7. Full-width parentheses consistency (additional)
Use full-width （） consistently around Chinese text; don't mix full-width and
half-width parenthesis characters in the same pair.

- Incorrect: 这是一个例子(仅供参考）。
- Correct: 这是一个例子（仅供参考）。
