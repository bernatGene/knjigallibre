tmux new-session -d -s foo 'exec python stream.py'
# tmux send-keys 'bundle exec thin start' 'C-m'
# tmux rename-window 'Foo'
tmux select-window -t foo:0
tmux split-window -h 'exec python streamclient.py'
# tmux send-keys 'bundle exec compass watch' 'C-m'
# tmux split-window -v -t 0 'exec pfoo'
# tmux send-keys 'rake ts:start' 'C-m'
# tmux split-window -v -t 1 'exec pfoo'
tmux -2 attach-session -t foo