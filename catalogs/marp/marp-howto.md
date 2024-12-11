---
marp: true
title: Howto use MARP
description: HOWTO use MARP
author: Bernhard Wallisch (bernhard_wallisch@hotmail.com)
keywords: Markdown, MARP, MARPIT
url: https://codepunx.wordpress.com
theme: gaia
style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
paginate: true
footer: 'MarkSlide Go'
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---
<!--
_paginate: skip
_footer: ''
_class : lead
-->
# Howto use MARP

see guide from [@marp-team/marp-cli](https://www.npmjs.com/package/@marp-team/marp-cli#basic-usage)

---
### Convert a markdown into HTML

The passed markdown will be converted to HTML file by default.

```shell
npx marp slide-deck.md -o output.html
```

The -o parameter is optional, if left the output file will be generated in the same directory.

---
### Convert a markdown into PDF

If you passed --pdf option or the output filename specified by --output (-o) option ends with .pdf, Marp CLI will try to convert Markdown into PDF file through the browser.

```shell
npx marp --pdf --allow-local-files slide-deck.md
npx marp --allow-local-files slide-deck.md -o converted.pdf
```

Remarks: use *--allow-local-files* to allow e.g. local image files to be rendered.

---
### Convert a markdown into PDF (samples)

Samples to generate PDF with outlines and notes:

```shell
npx marp --html --pdf --pdf-outlines --pdf-outlines.pages=false \
--pdf-notes --allow-local-files getting-started.md -o getting-started.pdf
```

Remark: additionally add the --html option to enable html-tag rendering (which is necessary for theme-tweaks and multi-column content)

---
### Convert a markdown into PowerPoint

PPTX conversion to create PowerPoint document is available by passing --pptx option or specify the output path with PPTX extension.

```shell
npx marp --pptx slide-deck.md
npx marp slide-deck.md -o converted.pptx
```

---
## Write Slide-Decks

see [Marpit Markdown](https://marpit.marp.app/markdown)

Slide separation:
Use *---* as slide separator, don't forget the empty line before and after the *---*
```shell
---
```
The first header (#) is the slide title

---

When the contents in a slide is cropped-off because too long, you may adjust the font-size with the following tweak:

```html
<style scoped>section { font-size: 20px; }</style>
```
