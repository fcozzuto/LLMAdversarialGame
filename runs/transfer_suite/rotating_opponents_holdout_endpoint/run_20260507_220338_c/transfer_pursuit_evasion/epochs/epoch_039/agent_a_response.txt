def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role_s = str(observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role_s) or ("chase" in role_s) or ("hunter" in role_s)
    is_evader = ("evad" in role_s) or ("run" in role_s) or ("away" in role_s) or ("escape" in role_s)
    if not (is_pursuer or is_evader):
        is_pursuer = True  # default: be the one that tries to capture

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                m += 1
        return m

    def edge_tendency(x, y):
        # prefer moving inward as pursuer; as evader, avoid tight edges
        d_left = x
        d_right = (w - 1 - x)
        d_top = y
        d_bot = (h - 1 - y)
        return min(d_left, d_right, d_top, d_bot)

    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        e = edge_tendency(nx, ny)

        if is_pursuer:
            # minimize distance, keep good mobility; small bias to avoid hugging edges
            val = -d * 10 + mob * 3 + e * 0.25
            better = (best_val is None) or (val > best_val)
        else:
            # maximize distance, keep mobility; avoid low edge distance (being cornered)
            val = d * 10 + mob * 3 + e * 0.75
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]