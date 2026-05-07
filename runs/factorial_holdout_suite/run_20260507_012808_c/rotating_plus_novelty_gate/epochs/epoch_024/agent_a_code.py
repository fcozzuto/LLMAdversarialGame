def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if p is None:
            continue
        try:
            x, y = p
        except Exception:
            continue
        obstacles.add((x, y))

    resources = observation.get("resources") or []

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = [0, 0]
    bestv = -10**18

    if resources:
        targets = resources
    else:
        targets = [((w - 1) // 2, (h - 1) // 2)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        nearest = 10**9
        for tx, ty in targets:
            d = md(nx, ny, tx, ty)
            if d < nearest:
                nearest = d

        oppd = md(nx, ny, ox, oy)
        v = -nearest * 10 + oppd

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best