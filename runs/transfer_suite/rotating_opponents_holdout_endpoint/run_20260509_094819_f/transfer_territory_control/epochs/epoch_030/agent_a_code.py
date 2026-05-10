def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    if (sx, sy) in obstacles:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Bias: we want to expand to unclaimed, but avoid flipping into opponent too often.
    # Also, if unclaimed is scarce, fall back to consolidating toward center-ish frontier.
    unclaimed_list = list(unclaimed)
    have_unclaimed = len(unclaimed_list) > 0

    def nearest_unclaimed_dist2(x, y):
        best = 10**9
        for ux, uy in unclaimed_list:
            dx, dy = ux - x, uy - y
            d = dx * dx + dy * dy
            if d < best:
                best = d
        return best if best < 10**9 else 10**9

    def cell_score(x, y):
        if (x, y) in obstacles:
            return -10**8
        k = 0
        if (x, y) in unclaimed:
            k += 40
        if (x, y) in selfT:
            k += 6
        if (x, y) in oppT:
            k -= 18  # flipping can be good, but too risky vs center-claimer
        # Mild center pressure (territory control tends to expand toward center)
        k -= int(2 * ((x - cx) * (x - cx) + (y - cy) * (y - cy)) ** 0.5)
        if have_unclaimed:
            # Prefer cells that reduce distance to nearest unclaimed (large weight to be deterministic and decisive)
            k -= int(0.7 * nearest_unclaimed_dist2(x, y) ** 0.5)
        return k

    best_s = -10**18
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        s = cell_score(nx, ny)
        # Deterministic tie-break: prefer staying near center and lexicographically smallest move
        tie = (0, 0) if (dx, dy) == (0, 0) else (abs(nx - cx) + abs(ny - cy),)
        if s > best_s or (s == best_s and (tie, dx, dy) < (0 if best == (0, 0) else (abs(best[0] - cx) + abs(best[1] - cy),), best[0], best[1])):
            best_s = s
            best = (dx, dy)

    return [int(best[0]), int(best[1])]