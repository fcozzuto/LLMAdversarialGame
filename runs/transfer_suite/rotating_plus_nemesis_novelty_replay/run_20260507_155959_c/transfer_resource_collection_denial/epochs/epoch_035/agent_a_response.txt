def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    # Resource-denier response: either race their nearest resource if we can tie/overtake,
    # otherwise go for the resource that hurts their relative progress most.
    nearest_opp = min(res, key=lambda p: md(ox, oy, p[0], p[1]))
    tx, ty = nearest_opp
    du = md(sx, sy, tx, ty)
    do = md(ox, oy, tx, ty)

    if du <= do:
        target = (tx, ty)
    else:
        # Maximize (opponent distance - our distance), then prefer closer for us as a tiebreak.
        target = max(res, key=lambda p: (md(ox, oy, p[0], p[1]) - md(sx, sy, p[0], p[1]), -md(sx, sy, p[0], p[1]), -p[0], -p[1]))

    tx, ty = target
    # Greedy step toward target with deterministic tie-break.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = md(nx, ny, tx, ty)
        key = (d, abs((tx - nx)) + abs((ty - ny)) == 0, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]