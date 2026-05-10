def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    unclaimed = observation.get("unclaimed_cells") or []
    if not unclaimed:
        return [0, 0]
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    candidates = []
    best_adj = -1
    for p in unclaimed:
        x, y = int(p[0]), int(p[1])
        if not ok(x, y):
            continue
        adj = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_t:
                    adj = 1
                    break
            if adj:
                break
        candidates.append((x, y, adj))
        if adj > best_adj:
            best_adj = adj

    focus = [c for c in candidates if c[2] == best_adj] if best_adj > 0 else candidates
    focus.sort()  # deterministic tie-break baseline

    best = None
    best_sc = -10**18
    for x, y, adj in focus:
        d_us = man(sx, sy, x, y)
        d_opp = man(ox, oy, x, y)
        edge = 1 if (x == 0 or y == 0 or x == w - 1 or y == h - 1) else 0
        dist_center = abs(x - cx) + abs(y - cy)
        sc = 5.0 * (d_opp - d_us) + 3.0 * adj + 0.4 * edge - 0.15 * dist_center
        if sc > best_sc:
            best_sc = sc
            best = (x, y)

    tx, ty = best if best is not None else (w // 2, h // 2)
    best_move = [0, 0]
    best_md = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        md = man(nx, ny, tx, ty)
        if md < best_md:
            best_md = md
            best_move = [dx, dy]
        elif md == best_md:
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]