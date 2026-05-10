def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obs_blocked = lambda x, y: (x, y) in obstacles

    def neigh4(x, y):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and not obs_blocked(nx, ny):
                yield nx, ny

    # Prefer unclaimed cells adjacent to our territory (frontier). Fallback to any unclaimed.
    frontier = []
    for x, y in uncla:
        for nx, ny in neigh4(x, y):
            if (nx, ny) in selfT:
                frontier.append((x, y))
                break
    targets = frontier if frontier else list(uncla)

    oppx, oppy = observation.get("opponent_position", [w - 1, h - 1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if (dx != 0 or dy != 0) and (not inb(nx, ny) or obs_blocked(nx, ny)):
            continue

        base = 0.0
        if (nx, ny) in selfT:
            base = 0.3
        elif (nx, ny) in uncla:
            base = 2.6
        elif (nx, ny) in oppT:
            base = 3.9  # can flip on entry
        else:
            base = 1.0  # unknown/empty

        # Frontier adjacency bonus (more immediate expansion).
        frontier_adj = 0
        for ax, ay in neigh4(nx, ny):
            if (ax, ay) in selfT:
                frontier_adj += 1
        base += 0.18 * frontier_adj

        # Strategic positioning: move toward the nearest target, but avoid being too close to opponent.
        if targets:
            mind = min(dist(nx, ny, tx, ty) for tx, ty in targets)
        else:
            mind = dist(nx, ny, w - 1, h - 1)
        base += 0.55 * (10 - min(mind, 10))  # reward reducing distance

        base -= 0.10 * dist(nx, ny, oppx, oppy)

        # Small tie-break: prefer moves that change position (unless score already equal).
        if (dx, dy) != (0, 0):
            base += 0.02

        if base > best_score:
            best_score = base
            best_move = [dx, dy]

    return best_move