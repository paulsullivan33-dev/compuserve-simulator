import textwrap


def wrap_terminal_text(text, width):
    lines = []
    for logical_line in str(text).split("\n"):
        if len(logical_line) <= width:
            lines.append(logical_line)
        else:
            lines.extend(textwrap.wrap(
                logical_line, width=width, replace_whitespace=False,
                drop_whitespace=True, break_long_words=True,
                break_on_hyphens=False,
            ))
    return lines


def header_line(service, page, width):
    padding = max(1, width - len(service) - len(page))
    return service + (" " * padding) + page


def menu_lines(service, page, title, options, width, return_label="M  Return to previous menu"):
    lines = [header_line(service, page, width), title, "-" * min(len(title), width)]
    lines.extend(f"{key}  {label}" for key, label in options.items())
    lines.extend(["", return_label, ""])
    rendered = []
    for line in lines:
        rendered.extend(wrap_terminal_text(line, width))
    return rendered
