def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obs_pen(x, y):
        pen = 0
        for ox2, oy2 in obstacles:
            if abs(ox2 - x) <= 1 and abs(oy2 - y) <= 1:
                pen += 4 if (ox2, oy2) == (x, y) else 2
        return pen

    # Choose a deterministic "best" target for this turn.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can secure (strictly closer or opponent not immediate).
        immediate = (do <= 1)
        key = (1 if (ds <= do and not immediate) else 0, (do - ds), -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # Evaluate possible moves; pick one that improves reaching target while avoiding obstacles and denying opponent proximity.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        # If opponent is already very close, prioritize moves that increase their chance to not reach immediately.
        opp_pressure = cheb(ox, oy, nx, ny) <= 1
        score = 1000 - ds_new * 20 + (do_now - ds_new) * 8
        score -= near_obs_pen(nx, ny)
        if opp_pressure:
            score -= 35
        # Slight tie-break to remain deterministic and stable.
        score -= (abs(dx) + abs(dy)) * 0.5
        key2 = score
        if best_score is None or key2 > best_score:
            best_score = key2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]