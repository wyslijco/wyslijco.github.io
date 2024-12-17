from labels import Label


def has_label(issue, label: Label):
    return any([l for l in issue.labels if l.name == label])
