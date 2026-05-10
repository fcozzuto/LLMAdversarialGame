def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    def adj4_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in S: c += 1
        return c
    # Prefer cells that are at/near the opponent frontier; otherwise expand to unclaimed.
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_terr:
            score = 1.0 * adj4_count(nx, ny, self_terr)
        elif (nx, ny) in opp_terr:
            score = 60.0 + 6.0 * adj4_count(nx, ny, opp_terr)
        elif (nx, ny) in unclaimed:
            score = 22.0 + 3.0 * adj4_count(nx, ny, opp_terr)
        else:
            score = 8.0 * adj4_count(nx, ny, opp_terr)  # likely empty/neutral
        # Defensive bias: avoid stepping into "holes" far from own territory when possible.
        own_adj = adj4_count(nx, ny, self_terr)
        if own_adj == 0 and (nx, ny) not in unclaimed:
            score -= 6.0
        # Deterministic tie-break by direction order (dirs already fixed).
        key = (-score, abs(nx - (w - 1)) + abs(ny - (h - 1)) + abs(nx) + abs(ny), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best