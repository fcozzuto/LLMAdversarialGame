def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Targets: prefer immediate entry into opponent territory, then unclaimed, then edges next to opponent.
    opp_neighbors = set()
    for (x, y) in opp_terr:
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = x + ax, y + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                    opp_neighbors.add((tx, ty))

    best = None
    best_key = (-10**9, 10**9, 0)  # (value, dist_to_opp, dx/dy tie-breaker)

    for dx, dy, nx, ny in moves:
        val = 0.0
        if (nx, ny) in opp_terr:
            val += 6.5  # direct flipping
        elif (nx, ny) in unclaimed:
            val += 3.2  # claim
        elif (nx, ny) in self_terr:
            val += 1.0  # slow growth, safer
        else:
            val += 0.4  # empty

        if (nx, ny) in opp_neighbors:
            val += 2.0  # likely frontier capture
        if (nx, ny) in resources:
            val += 2.8

        # Mild pressure towards opponent to keep territory momentum.
        dist = abs(nx - ox) + abs(ny - oy)
        val += (7.0 - 0.7 * dist)  # higher when closer

        # Avoid committing too deep where opponent could surround next.
        if (nx, ny) in self_terr and len([1 for ax in (-1, 0, 1) for ay in (-1, 0, 1) if (ax or ay) and 0 <= nx + ax < w and 0 <= ny + ay < h and (nx + ax, ny + ay) in opp_terr]) > 0:
            val -= 0.8

        key = (val, dist, dx * 10 + dy)
        if key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]