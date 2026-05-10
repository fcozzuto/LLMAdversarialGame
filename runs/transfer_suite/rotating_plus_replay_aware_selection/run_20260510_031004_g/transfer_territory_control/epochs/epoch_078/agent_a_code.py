def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    dirs_pref = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]

    resources = observation.get("resources", []) or []
    if resources:
        rx, ry = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        rx, ry = (w - 1) // 2, (h - 1) // 2

    best = None
    for dx, dy in dirs_pref:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = abs(nx - rx) + abs(ny - ry)
        d_opp = abs(nx - ox) + abs(ny - oy)
        score = (d_opp, -d_self)  # maximize distance from opponent, then approach target
        if best is None or score > best[0]:
            best = (score, [dx, dy])

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best[1]