def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y): 
        return 0 <= x < w and 0 <= y < h

    selfT = set(tuple(t) for t in observation.get("self_territory") or [])
    oppT = set(tuple(t) for t in observation.get("opponent_territory") or [])
    unclaimed = set(tuple(c) for c in observation.get("unclaimed_cells") or [])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        candidates.append((dx, dy, nx, ny))

    # If we can flip directly into opponent territory, do it deterministically.
    for dx, dy, nx, ny in candidates:
        if (nx, ny) in oppT:
            return [dx, dy]

    # Frontier targets: unclaimed cells adjacent to our territory.
    frontier = set()
    for (x, y) in selfT:
        for ddx, ddy in dirs:
            ax, ay = x + ddx, y + ddy
            if inside(ax, ay) and (ax, ay) in unclaimed:
                frontier.add((ax, ay))
    targets = list(frontier) if frontier else list(unclaimed)

    if not targets:
        # No expansion possible; try to move away from opponent position to avoid being taken.
        best = (0, 0)
        bestd = -1
        for dx, dy, nx, ny in candidates:
            d = max(abs(nx - ox) + abs(ny - oy), abs(nx - sx) + abs(ny - sy))
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Score targets by closeness, with slight preference for edges to fight sweeper.
    def edge_score(t):
        x, y = t
        return min(x, y, w - 1 - x, h - 1 - y)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in candidates:
        # Minimal heuristic distance from next cell to chosen targets.
        mind = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < mind:
                mind = d
        # Prefer smaller mind; also prefer targets near edges by using edge_score (smaller is closer).
        # We incorporate opponent proximity to reduce suicidal pushes into their sweep path.
        prox_pen = abs(nx - ox) + abs(ny - oy)
        val = -mind * 10 - edge_score(min(targets, key=lambda t: abs(t[0]-nx)+abs(t[1]-ny))) - prox_pen * 0.2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]