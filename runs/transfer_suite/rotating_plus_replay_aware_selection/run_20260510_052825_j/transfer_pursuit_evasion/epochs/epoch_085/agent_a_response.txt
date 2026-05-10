def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role) or ("hunter" in role) or (not evader)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    obs = list(blocked)

    def obs_pen(nx, ny):
        if not obs:
            return 0
        md = 10**9
        for x, y in obs:
            dd = dist2(nx, ny, x, y)
            if dd < md:
                md = dd
        # Stronger penalty when closer to obstacles
        return 1000 // (1 + md)

    best = None
    best_score = -10**18 if pursuer else 10**18

    if pursuer:
        # chase: minimize distance, avoid obstacles
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            score = d + obs_pen(nx, ny)
            if best is None or score < best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
    else:
        # evade: maximize distance, bias toward a far corner deterministically
        tc = None
        best_corner_dist = -1
        for cx, cy in corners:
            dd = dist2(sx, sy, cx, cy)
            if dd > best_corner_dist:
                best_corner_dist = dd
                tc = (cx, cy)
        cx, cy = tc
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d_opp = dist2(nx, ny, ox, oy)
            d_corner = dist2(nx, ny, cx, cy)
            score = -d_opp - (d_corner // 4) + obs_pen(nx, ny)
            if best is None or score < best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]