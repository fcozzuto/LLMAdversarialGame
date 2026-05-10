def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def n8(x, y):
        res = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny):
                        res.append((nx, ny))
        return res

    frontier = []
    for (x, y) in unclaimed:
        if any(p in opp_t for p in n8(x, y)):
            frontier.append((x, y))

    targets = frontier if frontier else list(unclaimed)
    if not targets:
        # If no unclaimed, try to contest near opponent territory.
        # Move to neighbor that is closest to any opponent territory cell.
        opp_cells = list(opp_t) if opp_t else [(ox, oy)]
        tx, ty = min(opp_cells, key=lambda p: (p[0] - sx) ** 2 + (p[1] - sy) ** 2)
    else:
        # Prefer frontier cells; otherwise nearest unclaimed.
        tx, ty = min(targets, key=lambda p: ( (p[0] - sx) ** 2 + (p[1] - sy) ** 2, 0 if p in frontier else 1 ))

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            val = -10**6
        else:
            cell = (nx, ny)
            val = 0
            if cell in opp_t:
                val += 2.5
            elif cell in unclaimed:
                val += 1.3
            elif cell in self_t:
                val += 0.2
            # Move toward target; small tie-breaker toward reducing distance to opponent.
            val += -0.01 * ((nx - tx) ** 2 + (ny - ty) ** 2)
            val += -0.005 * ((nx - ox) ** 2 + (ny - oy) ** 2)
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]