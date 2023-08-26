tmux new-session -d -s foo 'exec python typetest.py'
tmux select-window -t foo:0
tmux split-window -h 'exec python typtestclient.py'
tmux -2 attach-session -t foo