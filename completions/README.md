Command Line Auto-Completions
=============================
Because typing is no fun

Zsh
---
In the `completions/zsh` directory is a file to help with auto-completions in
`zsh`. In order to get completions working with `shovel` and `zsh`:

1. Tell zsh where to find the script `_shovel`. For example, put it at
    `~/.zsh/completion/_shovel` and somewhere in .zshrc before you call
    `compinit` add the commond `fpath=(~/.zsh/completion/ $fpath)`.
2. Navigate to a directory where you've tasks in `shovel.py` or under
    `shovel/`, and hit `TAB` twice. Or, type the first couple letters of a
    command and hit `TAB` once. Boom.

Bash
----
In the `completions/bash` directory is a file to help with auto-completions in `bash`.  Installation:

1.  Install [bash-completion](https://github.com/scop/bash-completion) if you haven't already.  
  `brew install bash-completion@2`

2.  Copy `completions/bash/shovel` to your local bash completions directory.

```
mkdir -p ~/.local/share/bash-completion/completions

cp completions/bash/shovel ~/.local/share/bash-completion/completions/shovel
```

3.  Open a new terminal so the completions file will be sourced.

4.  Navigate to a directory where tasks are in `shovel.py` or `shovel/` and hit `TAB` twice.  Or type the first couple letters of a command and hit `TAB` once.  Baam!
