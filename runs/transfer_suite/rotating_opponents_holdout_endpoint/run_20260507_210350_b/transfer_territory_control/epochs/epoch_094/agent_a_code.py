def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def clamp01(v):
        if v < 0: 
            return 0.0
        if v > 1:
            return 1.0
        return float(v)

    # Frontier bias: if we can step into a cell adjacent to any unclaimed, prefer it.
    def frontier_score(x, y):
        best = 0.0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                best = max(best, 1.0)
        return best

    best_sc = -10**18
    best = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            sc = -10**12
        else:
            # Distance-to-center improvement
            d0 = abs(sx - cx) + abs(sy - cy)
            d1 = abs(nx - cx) + abs(ny - cy)
            center_gain = d0 - d1

            # Territory target preference
            if (nx, ny) in opp_t:
                # allow flipping but only if it moves meaningfully towards center / frontier
                sc = 900 + 2200 * clamp01(center_gain / 3.0) + 500 * frontier_score(nx, ny)
            elif (nx, ny) in unclaimed:
                sc = 1400 + 900 * clamp01(center_gain / 3.0) + 700 * frontier_score(nx, ny)
            elif (nx, ny) in self_t:
                sc = 60 + 120 * clamp01(center_gain / 3.0) + 200 * frontier_score(nx, ny)
            else:
                sc = 10 + 100 * clamp01(center_gain / 3.0)

            # Slight preference for progressing away from corners early
            corner_pen = (min(sx, w - 1 - sx) + min(sy, h - 1 - sy)) - (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
            sc += 30 * clamp01(corner_pen / 2.0)

        # Deterministic tie-break: fixed order of dirs already
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]