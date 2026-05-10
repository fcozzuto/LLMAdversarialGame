def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    opp = observation.get("opponent_territory") or []
    opp_set = set()
    for p in opp:
        if p and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    cand = []
    for p in unclaimed:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                cand.append((x, y))

    # If no unclaimed, still move toward center and away from opponent territory
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = 10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        center_dist = abs(nx - cx) + abs(ny - cy)

        # prefer cells closer to center; if unclaimed exist, prefer the best unclaimed in that direction
        target_boost = 0
        if cand:
            # deterministic: compute min center-weighted manhattan to unclaimed
            best = 10**9
            for tx, ty in cand:
                d = abs(nx - tx) + abs(ny - ty)
                if d < best:
                    best = d
            target_boost = best

        # avoid stepping into opponent-controlled area unless it improves central claim
        opp_dist = 10**9
        if opp_set:
            for ox, oy in opp_set:
                dd = abs(nx - ox) + abs(ny - oy)
                if dd < opp_dist:
                    opp_dist = dd
        else:
            opp_dist = 10**9

        on_opp = 1 if (nx, ny) in opp_set else 0

        # Lower is better: primarily center distance, then approach nearby unclaimed,
        # and discourage proximity/entry into opponent territory.
        val = center_dist * 10.0 + target_boost * 1.2 + (0 if opp_dist >= 3 else (3 - opp_dist)) * 3.0 + on_opp * 8.0

        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]