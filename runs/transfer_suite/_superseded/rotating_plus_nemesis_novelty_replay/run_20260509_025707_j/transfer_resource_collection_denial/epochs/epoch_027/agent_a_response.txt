def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick a target that we can win while adding pressure to contestable resources.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Positive when we are closer; we prefer winning targets.
        win = sd - od  # smaller is better (negative means we are closer)
        # Pressure: if opponent is very close, also prioritize blocking.
        pressure = (8 - min(8, od))
        # Avoid sticking too far; prefer not-too-distant routes.
        dist_pen = sd
        # Slight alignment bias to reduce giving alternate routes.
        align = 0
        if ry == oy: align -= 2
        if rx == ox: align -= 1
        key = (win, dist_pen, -pressure, rx * 8 + ry)
        if best is None or key < best[0]:
            best = (key, rx, ry, sd, od)

    _, tx, ty, _, _ = best

    # Greedy step: among valid moves, choose smallest (distance to target),
    # with a deterministic secondary objective to not fall into opponent-favored proximity.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_d = man(sx, sy, tx, ty)
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        # Opponent proximity to the same target; we prefer to keep distance high.
        opp_d = man(ox, oy, tx, ty)
        # Simple improvement metric; if we can't get closer, still move to reduce future distance.
        improve = nd - cur_d
        # Deterministic tie-break: keep moves ordered by deltas and coordinates.
        val = (improve, nd, -opp_d, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]