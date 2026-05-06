def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (0, 1), (-1, 1), (1, 1)]

    def md2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def cell_score(nx, ny):
        my_min = None
        op_min = None
        for rx, ry in resources:
            dmy = md2(nx, ny, rx, ry)
            dop = md2(ox, oy, rx, ry)
            if my_min is None or dmy < my_min:
                my_min = dmy
            if op_min is None or dop < op_min:
                op_min = dop
        # Prefer states where I'm closer to some resource than the opponent currently is.
        # Add a small repulsion from opponent if they're very close.
        my_opp_gap = (my_min - op_min) if my_min is not None and op_min is not None else 0
        opp_close = md2(nx, ny, ox, oy)
        risk = 0 if opp_close > 9 else 5 * (9 - opp_close)
        return my_opp_gap + risk + 0.01 * (nx * 0 + ny * 0)

    best = None
    best_move = [0, 0]
    # Deterministic tie-break: fixed move order; choose strictly lower score.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = cell_score(nx, ny)
        if best is None or sc < best:
            best = sc
            best_move = [dx, dy]

    return best_move