def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                unclaimed.append((x, y))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Prefer unclaimed frontier cells adjacent to our territory
    if unclaimed:
        frontier = []
        for x, y in unclaimed:
            if any(((x + dx, y + dy) in self_terr) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy):
                frontier.append((x, y))
        candidates = frontier if frontier else unclaimed
        # Deterministic heuristic: closer to us, then farther from opponent (to slow their advance)
        tx, ty = min(candidates, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), -(abs(c[0] - ox) + abs(c[1] - oy)), c[1], c[0]))
    else:
        tx, ty = ox, oy

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic "reject => stay"
            dx, dy = 0, 0
        # Greedy step toward target; tie-break by directions order already deterministic
        dist = abs(nx - tx) + abs(ny - ty)
        key = (dist, -abs(nx - ox) - abs(ny - oy), ny, nx, dx, dy)
        if best is None or key < best_key:
            best = (dx, dy)
            best_key = key
    return [int(best[0]), int(best[1])]