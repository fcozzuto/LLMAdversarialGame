def choose_move(observation):
    wx = observation.get('grid_width', 0)
    hy = observation.get('grid_height', 0)
    px, py = observation.get('self_position', (0, 0))
    oppx, oppy = observation.get('opponent_position', (0, 0))
    obstacles = set(map(tuple, observation.get('obstacles', [])))
    resources = set(map(tuple, observation.get('resources', [])))
    remaining = observation.get('remaining_resource_count', 0)
    score_self, score_opp = observation.get('scores', [0, 0])

    def move_towards(a, b):
        dx, dy = 0, 0
        if a[0] < b[0]:
            dx = 1
        elif a[0] > b[0]:
            dx = -1
        elif a[1] < b[1]:
            dy = 1
        elif a[1] > b[1]:
            dy = -1
        return dx, dy

    def is_safe(nx, ny):
        return (
            (nx, ny) not in obstacles and
            0 <= nx < wx and
            0 <= ny < hy
        )

    def safe_move(dx, dy):
        nx, ny = px + dx, py + dy
        return is_safe(nx, ny)

    resource_list = list(resources)
    if resource_list:
        resource_list.sort(key=lambda t: abs(t[0] - px) + abs(t[1] - py))
        for tx, ty in resource_list:
            dx, dy = move_towards((px, py), (tx, ty))
            if safe_move(dx, dy):
                return [dx, dy]

    dx, dy = move_towards((px, py), (oppx, oppy))
    if safe_move(dx, dy):
        return [dx, dy]

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
        if safe_move(dx, dy):
            return [dx, dy]
    return [0, 0]
