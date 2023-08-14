tmux new-session -d -s foo 'exec python stream.py'
tmux select-window -t foo:0
tmux split-window -h 'exec python streamclient.py'
tmux -2 attach-session -t foo