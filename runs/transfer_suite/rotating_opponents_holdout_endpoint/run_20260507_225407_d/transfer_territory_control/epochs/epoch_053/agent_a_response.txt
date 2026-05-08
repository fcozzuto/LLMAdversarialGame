def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    px, py = (observation.get("opponent_position") or [sx, sy])
    sx, sy, px, py = int(sx), int(sy), int(px), int(py)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        v = 0.0
        if (x, y) in unclaimed:
            v += 30.0
        if (x, y) in opp_terr:
            v += 12.0  # entering flips control, so capture value
        if (x, y) in self_terr:
            v -= 3.0   # prefer expansion
        if x == 0 or x == w - 1 or y == 0 or y == h - 1:
            v += 2.0
        # Move toward the opponent "frontier" by decreasing distance to opponent, but not into them blindly
        v += 0.7 * (abs(sx - px) + abs(sy - py) - (abs(x - px) + abs(y - py)))
        # Prefer moves that get closer to likely high-value cells (unclaimed or opponent territory)
        if unclaimed:
            # Use a deterministic coarse proxy: aim toward nearest among a few sampled candidates from sets
            # (sampling deterministically without randomness)
            bestd = 10**9
            bestx, besty = x, y
            # pick at most 12 candidates deterministically by ordering
            idx = 0
            for cx, cy in sorted(unclaimed)[:12]:
                d = abs(cx - x) + abs(cy - y)
                if d < bestd:
                    bestd, bestx, besty = d, cx, cy
                idx += 1
            v += -0.8 * bestd
        elif opp_terr:
            bestd = 10**9
            for cx, cy in sorted(opp_terr)[:12]:
                d = abs(cx - x) + abs(cy - y)
                if d < bestd:
                    bestd = d
            v += -0.8 * bestd
        return v

    best = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = cell_value(nx, ny)
        # deterministic tie-break: prefer larger v, then move order in dirs
        if v > best:
            best = v
            best_move = [dx, dy]
    return best_move