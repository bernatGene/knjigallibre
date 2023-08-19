tmux new-session -d -s foo 'exec python controlmode.py'
tmux select-window -t foo:0
tmux split-window -h 'exec python controlmodeclient.py'
tmux -2 attach-session -t foo