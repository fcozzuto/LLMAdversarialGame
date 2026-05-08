def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c is not None and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c is not None and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c is not None and len(c) >= 2)

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return not inb(x, y) or (x, y) in obs
    def md(a, b, x, y): return abs(x - a) + abs(y - b)

    frontier = set()
    if self_t:
        for x, y in self_t:
            for dx, dy in dirs[1:]:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
    if not frontier:
        frontier = set(unclaimed)

    # Deterministic tie-break: highest score, then prefer staying still if close, then smaller dx,dy lexicographically.
    def move_score(nx, ny):
        if blocked(nx, ny):
            return -10**9
        if (nx, ny) in opp_t:
            base = 120
        elif (nx, ny) in unclaimed:
            base = 70
        elif (nx, ny) in self_t:
            base = 35
        else:
            base = 10

        # Prefer moving toward frontier, and away from the opponent position a bit to avoid easy flips.
        if frontier:
            d = min(md(nx, ny, fx, fy) for fx, fy in frontier)
            base += max(0, 80 - d * 5)
        base -= md(nx, ny, ox, oy) // 2
        return base

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = move_score(nx, ny)
        if sc > best_score:
            best_score, best_move = sc, (dx, dy)
        elif sc == best_score:
            if (dx, dy) == (0, 0):
                best_move = (dx, dy)
            elif best_move != (0, 0) and (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]