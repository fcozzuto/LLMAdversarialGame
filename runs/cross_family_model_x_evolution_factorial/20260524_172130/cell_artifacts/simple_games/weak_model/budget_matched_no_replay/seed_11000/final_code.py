def choose_move(observation):
    w, h = observation['grid_width'], observation['grid_height']
    px, py = observation['self_position']
    def move_toward(target):
        dx = target[0] - px
        dy = target[1] - py
        return [(dx > 0) - (dx < 0), (dy > 0) - (dy < 0)]
    targets = observation.get('resources', [])
    if targets:
        t = min(targets, key=lambda p: abs(p[0]-px)+abs(p[1]-py))
        return move_toward(t)
    enemies = observation.get('opponent_position', [])
    if enemies:
        return move_toward(enemies)
    return [0, 0]
