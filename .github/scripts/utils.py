from labels import Label


def has_label(issue, label: Label):
    return any([ilabel for ilabel in issue.labels if ilabel.name == label])
