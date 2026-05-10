def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Prefer expanding our frontier, capturing unclaimed, then attacking opponent by adjacency.
    best = None
    best_val = -10**18

    for dx, dy, nx, ny in candidates:
        val = 0
        # Base target type
        if (nx, ny) in selfT:
            val += 2
        elif (nx, ny) in uncla:
            # more valuable if near our territory and near edges
            val += 10
        elif (nx, ny) in oppT:
            val += 18  # flipping on entry
        else:
            # in case it's not listed, treat as neutral/unknown
            val += 0

        # Frontline bonus: moving adjacent to our territory helps growth/secure
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px, py = nx + ax, ny + ay
            if (px, py) in selfT:
                val += 5
            if (px, py) in oppT:
                val += 4  # getting close to opponent territory

        # Distance shaping
        d_self = abs(nx - sx) + abs(ny - sy)
        val -= d_self * 0.2  # prefer local moves but allow expansion
        d_opp = abs(nx - ox) + abs(ny - oy)
        val -= d_opp * 0.05  # keep pressure towards opponent

        # Edge control: bias towards outer ring unclaimed
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        if edge:
            val += 2.5

        # Discourage stepping into opponent-owned cell too late unless it's adjacent advantage
        if (nx, ny) in oppT:
            val += 2 if any((nx + ax, ny + ay) in oppT for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1))) else 0

        # Deterministic tie-break: fixed ordering by dx,dy
        key = (val, -dx, -dy)
        if key > (best_val, 0, 0):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]