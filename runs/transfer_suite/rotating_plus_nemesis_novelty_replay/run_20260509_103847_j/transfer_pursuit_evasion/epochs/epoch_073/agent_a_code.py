def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if (sx, sy) == (ox, oy):
        return [0, 0]

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    pref = {(1, 0): 0, (-1, 0): 0, (0, 1): 0, (0, -1): 0,
            (1, 1): 1, (1, -1): 1, (-1, 1): 1, (-1, -1): 1,
            (0, 0): 2}

    cands = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue_ok = ok(sx, sy)
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            if ok(nx, ny):
                cands.append((dx, dy))

    if not cands:
        return [0, 0]

    def score(nx, ny):
        ddx = ox - nx
        ddy = oy - ny
        md = abs(ddx) + abs(ddy)
        ed = ddx * ddx + ddy * ddy
        if is_evader:
            # maximize distance; slightly prefer moving away in the dominant axis
            away_bonus = 0
            if abs(ox - sx) >= abs(oy - sy):
                away_bonus = (1 if (dx_dir(nx, sx, ox)) else 0)
            return (md * 10) + ed + (away_bonus)
        else:
            # minimize distance; prefer tightening both axes for zigzag interceptions
            signx = 1 if ox > nx else (-1 if ox < nx else 0)
            signy = 1 if oy > ny else (-1 if oy < ny else 0)
            align = (1 if signx == int((ox > sx)) else 0) + (1 if signy == int((oy > sy)) else 0)
            return (md * 10) + ed - (align * 0.5)

    def dx_dir(nx, sx0, ox0):
        # deterministic helper for evader: whether moved to increase x-separation
        return abs(ox0 - nx) > abs(ox0 - sx0)

    best = None
    bestv = None
    for dx, dy in sorted(cands, key=lambda t: pref.get(t, 9)):
        nx, ny = sx + dx, sy + dy
        v = score(nx, ny)
        if best is None:
            best, bestv = (dx, dy), v
        else:
            if is_evader:
                if v > bestv:
                    best, bestv = (dx, dy), v
            else:
                if v < bestv:
                    best, bestv = (dx, dy), v
    return [int(best[0]), int(best[1])]