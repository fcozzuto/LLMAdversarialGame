def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def to_set(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8 = moves

    if (sx, sy) in obstacles:
        return [0, 0]

    # Build frontier: unclaimed cells adjacent to our territory (8-neigh)
    frontier = []
    if selfT and unclaimed:
        for (x, y) in unclaimed:
            for dx, dy in neigh8:
                nx, ny = x - dx, y - dy
                if (nx, ny) in selfT:
                    frontier.append((x, y))
                    break

    # Decide target: prefer frontier far from opponent; else unclaimed closer to opponent to contest edge
    if frontier:
        tx, ty = max(frontier, key=lambda p: (abs(p[0] - ox) + abs(p[1] - oy), -(abs(p[0] - sx) + abs(p[1] - sy)), p[0], p[1]))
    elif unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - ox) + abs(p[1] - oy), abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    elif oppT:
        # If no unclaimed, push directly into opponent territory
        tx, ty = min(oppT, key=lambda p: abs(p[0] - ox) + abs(p[1] - oy))
    else:
        return [0, 0]

    # Choose next move that reduces distance to target, avoids obstacles, and slightly avoids entering opponent territory unless chasing
    opp_chase = bool(unclaimed)  # when unclaimed exists, we want contest rather than retreat
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        entering_opp = (nx, ny) in oppT
        du = abs(tx - nx) + abs(ty - ny)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        key = (du, (0 if (not entering_opp or opp_chase) else 1), -(dist_to_opp), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]