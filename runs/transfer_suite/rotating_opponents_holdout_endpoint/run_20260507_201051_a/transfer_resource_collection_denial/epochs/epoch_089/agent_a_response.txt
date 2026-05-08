def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w); h = int(h)
    except:
        w = 8; h = 8

    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = sp if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = op if isinstance(op, (list, tuple)) and len(op) >= 2 else (w - 1, h - 1)
    try:
        sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    except:
        sx = 0; sy = 0; ox = w - 1; oy = h - 1

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x = int(p[0]); y = int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x = int(p[0]); y = int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a target that we can contest: maximize (opp advantage) while arriving sooner.
    # score = (opp_d - self_d) - 0.15*self_d - 0.05*sum_coord_bias for tie-break
    best_resource = resources[0]
    best_score = None
    for (x, y) in resources:
        self_d = md(sx, sy, x, y)
        opp_d = md(ox, oy, x, y)
        self_bias = x + y
        sc = (opp_d - self_d) - 0.15 * self_d - 0.05 * self_bias
        if best_score is None or sc > best_score:
            best_score = sc
            best_resource = (x, y)

    tx, ty = best_resource

    # Choose move that improves contest position for that target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        self_d2 = md(nx, ny, tx, ty)
        opp_d2 = md(ox, oy, tx, ty)
        # Prefer faster capture and avoid giving opponent a much closer claim by increasing (opp_d - self_d)
        val = (opp_d2 - self_d2) - 0.2 * self_d2
        # Secondary tie-break: move along the target direction
        step_bias = -abs((tx - nx)) - abs((ty - ny))
        val = val * 1000 + step_bias
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]