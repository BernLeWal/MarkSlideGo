"""
Utility functions for markdown file operations.
"""

import os


def get_md_info(md_file:str) -> dict|None:
    info = {}
    if os.path.exists(md_file):
        try:
            first_line = ""
            with open(md_file, 'r', encoding='utf-8') as f:
                while line := f.readline():
                    line = line.strip()
                    if first_line == "" and line:
                        first_line = line.lstrip("# ").strip()
                        info['title'] = first_line
                        info['description'] = ""
                    elif line.startswith("# "):
                        return info # next section, stop processing
                    else: # add to description
                        info['description'] = info['description'] + line.strip() + "\n"
        except Exception:
            pass
    return info


def get_marp_info(md_file:str) -> dict|None:
  """Read the top of a markdown file and parse a Marp front-matter block.

  Reads up to 20 lines or until the second '---' marker. If a line
  'marp: true' is present in the block, returns a dict of parsed
  key: value pairs. Otherwise returns None.
  """
  if not os.path.exists(md_file):
    return None

  frontmatter = []
  inside = False
  max_lines = 20
  try:
    with open(md_file, 'r', encoding='utf-8') as f:
      for i in range(max_lines):
        line = f.readline()
        if line == '':
          break
        stripped = line.strip()
        if stripped == '---':
          if not inside:
            inside = True
            continue
          else:
            # end of frontmatter
            break
        if inside:
          frontmatter.append(stripped)
  except Exception:
    return None

  if not frontmatter:
    return None

  # parse lines as key: value
  result = {}
  found_marp_true = False
  for ln in frontmatter:
    if not ln or ln.startswith('#'):
      continue
    if ':' not in ln:
      # skip invalid lines
      continue
    key, val = ln.split(':', 1)
    key = key.strip()
    val = val.strip()
    # remove surrounding quotes if present
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
      val = val[1:-1]
    # convert booleans
    if val.lower() == 'true':
      parsed_val = True
    elif val.lower() == 'false':
      parsed_val = False
    else:
      parsed_val = val
    result[key] = parsed_val
    if key == 'marp' and parsed_val is True:
      found_marp_true = True

  if not found_marp_true:
    return None

  return result
