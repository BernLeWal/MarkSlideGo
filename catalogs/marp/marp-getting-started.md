---
marp: true
title: MARP Getting Started
description: A simple Getting-Started tutorial for writing slide-decks with MARP
author: Bernhard Wallisch (bernhard_wallisch@hotmail.com)
keywords: MARP, MARPIT, Slides
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

# MARP Getting Started

This is a title page.

---

# A simple content page

The following bullet-list is static (not animated):
- First item
- Second *kursive* item
- Third **bold** item

The following bullet-list is animated in (html presentation mode):
* First ***bold and cursive*** item (shown after mouse-click)
* Second item (shown after mouse-click)
* Third item (shown after mouse-click)

<!--
This is a comment block which will not show up in the slides directly,
but is available as notes in the html-presenter mode or as notes in PDF exports.
Furthermore it is useful for full-text search.
-->

---

# A mixed content page

- Links can be embedded like this: https://www.npmjs.com/package/@marp-team/marp-cli#basic-usage or this: [@marp-team/marp-cli](https://www.npmjs.com/package/@marp-team/marp-cli#basic-usage)
- Here is an embedded local image:  
    ![height:300px](marp-cli.gif)
- More properties of the image syntax see: https://marpit.marp.app/image-syntax

---

# Tables 

Use the common Markdown Syntax to include Tables:
| First column | Second column | Third Column |
|--------------|---------------|--------------|
| Row 1 Col 1 | Row 1 Col 2 | Row 1 Col 3 |
| *Row 2 Col 1* | **Row 2 Col 2** | ***Row 2 Col 3*** |
| Row 3 Col 1 | Row 3 Col 2 | Row 3 Col 3 |

---

# Sources and Codes

One of the very practical things compared to PPTX is that code can be treated easily within Markdown:

```shell
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt -y install ./google-chrome-stable_current_amd64.deb
google-chrome --version
```

```javascript
// the hello world program
console.log('Hello MARP!');
```

Code can also be included inline: ```./setup.sh```

---

# Multi-Column Slides

<div class="columns">
<div>

## Left Column
For multi-column slides we need the help of HTML and CSS (already included)

- an Item
- another Item

1. First Item
2. Second Item
3. Third Item

**ATTENTION**: Don't forget the linebreaks between the div-tags!

</div>
<div>

## Right Column
..but all known Markdown and HTML tag work well.

```csharp
// the hello world program
Console.WriteLine('Hello MARP!');
```

![width:400px](marp-cli.gif)

</div>
</div>

---

# Multi-Column Slides with an image

![bg left:30%](marp-generated-left.png)

Often there is the need to show an image and a text at the same time. In this case you may select the image as background image and put it to one side in order to use the place for the image optimal.

---

# Multi-Column Slides with an image

![bg right:30%](marp-generated-right.png)

Often there is the need to show an image and a text at the same time. In this case you may select the image as background image and put it to one side in order to use the place for the image optimal.

---
# Slide Generation

To generate this slide-deck run the following command in your shell:
```shell
../generate.sh marp-getting-started.md marp-getting-started.pdf
```
or
```shell
../generate.sh marp-getting-started.md marp-getting-started.html
```

---
<!--
_paginate: skip
_footer: ''
_class : lead
-->

# That's it for a quick start.
Have a nice time generate your own slides.
