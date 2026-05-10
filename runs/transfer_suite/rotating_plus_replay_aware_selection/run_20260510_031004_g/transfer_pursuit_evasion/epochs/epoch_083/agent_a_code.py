def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evade = ("evad" in role) or ("purs" in opp_role and "evad" not in role)

    resources = observation.get("resources") or []
    target_list = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                target_list.append((x, y))
        except Exception:
            pass

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if target_list:
        best = None
        bestv = None
        for dx, dy, nx, ny in candidates:
            md = 10**18
            for tx, ty in target_list:
                d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                if d < md: md = d
            v = md if evade else -md
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return [int(best[0]), int(best[1])]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = max(corners, key=lambda t: (t[0] - ox) * (t[0] - ox) + (t[1] - oy) * (t[1] - oy))
    ax, ay = (cx, cy) if evade else (ox, oy)

    best = candidates[0][:2]
    bestv = None
    for dx, dy, nx, ny in candidates:
        d = (nx - ax) * (nx - ax) + (ny - ay) * (ny - ay)
        v = -d if not evade else d
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]