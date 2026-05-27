def choose_move(observation):
    grid_width = observation.get('grid_width', 0)
    grid_height = observation.get('grid_height', 0)
    pos = observation.get('self_position', observation.get('own_position', (0, 0)))
    opp = observation.get('opponent_position', observation.get('opponent', (0, 0)))
    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    remaining = observation.get('remaining_resource_count', 0)
    scores = observation.get('scores', {})
    self_path = observation.get('self_path', [])
    opp_path = observation.get('opponent_path', [])

    if isinstance(pos, (list, tuple)) and len(pos) >= 2:
        x, y = pos[0], pos[1]
    else:
        x, y = 0, 0

    ox, oy = opp[0], opp[1] if isinstance(opp, (list, tuple)) and len(opp) >= 2 else (0, 0)

    def move_toward(cx, cy):
        dx = 0
        dy = 0
        if cx > x:
            dx = 1
        elif cx < x:
            dx = -1
        if cy > y:
            dy = 1
        elif cy < y:
            dy = -1
        return dx, dy

    best = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            dx, dy = move_toward(rx, ry)
            dist = abs(rx - x) + abs(ry - y)
            if best is None or dist < best[0]:
                best = (dist, dx, dy)

    if best is not None:
        return [best[1], best[2]]

    dx, dy = 0, 0
    if ox > x:
        dx = 1
    elif ox < x:
        dx = -1
    if oy > y:
        dy = 1
    elif oy < y:
        dy = -1

    if dx != 0 or dy != 0:
        return [dx, dy]

    return [0, 0]
