def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    if isinstance(unclaimed, dict):
        unclaimed = list(unclaimed.keys())
    unclaimed_set = set(tuple(p) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def adj_to_ours(x, y):
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self_terr:
                return True
        return False

    def adj_to_opps(x, y):
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr:
                return True
        return False

    # Prefer: expand from our frontier into unclaimed; if forced, take opponent at contact.
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        val = 0

        if cell in opp_terr:
            # Only steal if it's likely to flip into our frontier benefit (touch ours or open space).
            val += 420
            if adj_to_ours(nx, ny):
                val += 120
            if not adj_to_opps(nx, ny):
                val += 30
            # Avoid suiciding deep into their territory
            val -= 8 * (abs(nx - ox) + abs(ny - oy))
        elif cell in self_terr:
            val += 40  # keep stable
        elif cell in unclaimed_set:
            val += 160
            if adj_to_ours(nx, ny):
                val += 220
            else:
                val -= 40
            # Prefer cells closer to opponent-frontier distance (to later enable steals)
            val += 0.5 * (abs(sx - ox) + abs(sy - oy) - (abs(nx - ox) + abs(ny - oy)))
        else:
            # Some edge case: treat as neutral
            val += 5

        # Obstacle/edge pressure: slightly avoid moving away from center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        val -= 0.01 * dist2

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]