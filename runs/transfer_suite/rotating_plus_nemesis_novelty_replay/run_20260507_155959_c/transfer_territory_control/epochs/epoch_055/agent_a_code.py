def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    uc = []
    for c in unclaimed:
        if c is not None and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                uc.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_key = None

    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        if not inb(x, y) or (x, y) in obs:
            continue
        dopp = abs(x - ox) + abs(y - oy)
        if uc:
            dmin = 10**9
            for ux, uy in uc:
                d = abs(x - ux) + abs(y - uy)
                if d < dmin:
                    dmin = d
            key = (dmin * 1000 - dopp)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            dc = abs(x - cx) + abs(y - cy)
            key = (dc * 1000 - dopp)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]