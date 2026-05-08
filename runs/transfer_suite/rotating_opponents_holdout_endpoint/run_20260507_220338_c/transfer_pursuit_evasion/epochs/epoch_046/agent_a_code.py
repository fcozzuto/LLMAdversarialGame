def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            blocked.add((bx, by))

    role_s = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role_s for k in ("evad", "run", "away", "escape", "runner"))
    is_pursuer = ("purs" in role_s) or ("hunt" in role_s) or ("chase" in role_s)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy  # Chebyshev

    def safe(x, y):
        if (x, y) in blocked:
            return -10**9
        # keep away from obstacles: use nearest Manhattan
        dmin = 10**9
        for bx, by in blocked:
            d = abs(bx - x) + abs(by - y)
            if d < dmin:
                dmin = d
        if dmin == 10**9:
            dmin = 6
        border = min(x, y, w - 1 - x, h - 1 - y)
        return dmin + 0.4 * border

    best = None
    best_sc = -10**18

    cur_d = dist(sx, sy)
    # small deterministic bias to break ties
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            sc = -10**9
        else:
            nd = dist(nx, ny)
            delta = nd - cur_d
            # If pursuer: maximize distance decrease; If evader: maximize distance increase.
            goal = ( -delta if is_pursuer else delta )
            sc = 20.0 * goal + 0.9 * safe(nx, ny)
            # wall-runner counter: avoid getting too close to borders when evading
            if not is_pursuer:
                sc += 0.7 * (min(nx, ny, w - 1 - nx, h - 1 - ny))
            else:
                # pursuer prefers central-ish to avoid getting stalled by walls
                sc += 0.2 * (min(nx, ny, w - 1 - nx, h - 1 - ny))
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]