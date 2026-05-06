def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_list = observation.get("resources") or []
    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = legal[0]
    bestv = -10**18

    if resources:
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dop = manhattan(nx, ny, ox, oy)
            dres = 10**9
            for rx, ry in resources:
                d = manhattan(nx, ny, rx, ry)
                if d < dres:
                    dres = d
            v = -dres + 0.05 * dop
            if v > bestv:
                bestv = v
                best = (dx, dy)
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        farx, fary = max(corners, key=lambda t: manhattan(ox, oy, t[0], t[1]))
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = -manhattan(nx, ny, farx, fary) + 0.03 * manhattan(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)

    return [best[0], best[1]]