def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w or 8)
        h = int(h or 8)
    except:
        w, h = 8, 8
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def to_set(val):
        s = set()
        for p in (val or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    unclaimed = to_set(observation.get("unclaimed_cells"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        sc = 0
        if (nx, ny) in unclaimed:
            sc += 1000
        if (nx, ny) in oppT:
            sc += 300
        if (nx, ny) in selfT:
            sc -= 20

        md = abs(nx - ox) + abs(ny - oy)
        sc += (50 - md)

        border = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        sc += 10 if border else 0

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]
    return best