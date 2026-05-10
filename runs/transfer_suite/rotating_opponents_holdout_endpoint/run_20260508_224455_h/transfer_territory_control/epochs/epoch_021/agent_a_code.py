def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    def adj_to_opp(x, y):
        for nx, ny in neigh8(x, y):
            if (nx, ny) in opp_t:
                return True
        return False

    # Choose a strategic target: unclaimed cells adjacent to opponent, else opponent cells, else boundary expansion.
    frontier = [c for c in unclaimed if adj_to_opp(c[0], c[1])]
    if frontier:
        tx, ty = min(frontier, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[0], c[1]))
    elif opp_t:
        tx, ty = min(opp_t, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[0], c[1]))
    else:
        # Prefer expanding toward center and away from corners deterministically
        center = (w // 2, h // 2)
        candidates = list(unclaimed) if unclaimed else [(sx, sy)]
        tx, ty = min(candidates, key=lambda c: (abs(c[0] - center[0]) + abs(c[1] - center[1]), c[0], c[1]))

    best = (-10**9, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in opp_t:
            val += 500  # likely flip gain
        elif (nx, ny) in unclaimed:
            val += 120 if adj_to_opp(nx, ny) else 40
        elif (nx, ny) in self_t:
            val += 10
        else:
            val += 5

        # Approach target
        dist = abs(nx - tx) + abs(ny - ty)
        val += 200 - dist

        # Slightly avoid getting stuck on obstacles-adjacent squares
        if any((ax, ay) in obstacles for ax, ay in neigh8(nx, ny)):
            val -= 8

        # Tie-break deterministically by dir order
        if val > best[0]:
            best = (val, (dx, dy))

    if best[1] is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]