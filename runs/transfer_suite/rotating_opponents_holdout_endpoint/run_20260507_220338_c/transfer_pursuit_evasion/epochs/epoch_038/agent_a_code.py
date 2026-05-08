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
    role_o = str(observation.get("opponent_role", "") or "").lower()
    is_evader = ("evad" in role_s) or ("run" in role_s) or ("away" in role_s) or ("escape" in role_s) or ("evad" in role_o and "evad" not in role_s)

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

    def score_move(nx, ny):
        d = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # wall-run tendency: prefer moves that keep moving along the sign away/toward opponent
        tx = 0 if ox == nx else (1 if ox > nx else -1)
        ty = 0 if oy == ny else (1 if oy > ny else -1)
        if is_evader:
            # maximize distance; penalize stepping "toward" opponent
            # and prefer higher mobility to avoid traps.
            proj_toward = (nx - sx) * tx + (ny - sy) * ty
            return 5.0 * d - 2.0 * proj_toward + 0.3 * mob
        else:
            # minimize distance; avoid low-mobility squares.
            proj_toward = (nx - sx) * tx + (ny - sy) * ty
            return -5.0 * d + 2.0 * proj_toward + 0.25 * mob

    best = None
    best_s = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        s = score_move(nx, ny)
        # deterministic tie-break: fixed order already; keep first max/min
        if best_s is None or (is_evader and s > best_s) or ((not is_evader) and s > best_s):
            best_s = s
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]