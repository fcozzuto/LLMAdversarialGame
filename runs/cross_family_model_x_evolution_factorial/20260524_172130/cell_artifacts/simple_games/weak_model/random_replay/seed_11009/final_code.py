def choose_move(observation):
    agent_state = observation.get('agent', {})
    position = agent_state.get('position', (0, 0))
    resources = observation.get('resources', [])
    enemies = observation.get('enemies', [])
    territory = observation.get('territory', {})
    border = territory.get('border', [])

    targets = resources or enemies or border

    if targets:
        target = min(targets, key=lambda t: abs(t[0]-position[0]) + abs(t[1]-position[1]))
        dx = (target[0] - position[0])
        dy = (target[1] - position[1])
        dx = (dx > 0) - (dx < 0)
        dy = (dy > 0) - (dy < 0)
        return [dx, dy]
    else:
        return [1, 1]
