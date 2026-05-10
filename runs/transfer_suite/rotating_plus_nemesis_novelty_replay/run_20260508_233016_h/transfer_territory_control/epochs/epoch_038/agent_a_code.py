def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors(x, y):
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    # Aggressive: attack opponent frontier (unclaimed cells adjacent to opponent territory)
    opp_frontier = set()
    for (ox, oy) in opp_terr:
        for nx, ny in neighbors(ox, oy):
            if (nx, ny) in unclaimed:
                opp_frontier.add((nx, ny))

    # Fallback: nearest unclaimed
    targets = list(opp_frontier) if opp_frontier else list(unclaimed)
    if not targets:
        # Final fallback: move toward center to reduce being boxed in
        targets = [(w // 2, h // 2)]

    cx, cy = w // 2, h // 2
    targets.sort(key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), abs(c[0] - cx) + abs(c[1] - cy), c[0], c[1]))
    tx, ty = targets[0]

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        val = 0.0
        if cell in self_terr:
            val += 0.2  # keep stability
        if cell in unclaimed:
            val += 4.2 if cell == (tx, ty) else 2.6
        if cell in opp_terr:
            val += 2.8  # counterclaim by stepping into it (flip on entry)

        # Frontier pressure: closer to chosen target
        dist = abs(nx - tx) + abs(ny - ty)
        val += 3.0 / (1 + dist)

        # Prefer staying unblocked: penalize adjacency to obstacles
        adj_obs = 0
        for ax, ay in neighbors(nx, ny):
            if (ax, ay) in obstacles:
                adj_obs += 1
        val -= 0.25 * adj_obs

        # Small tie-break: prefer moves that decrease distance to target
        best_move_dist = abs(sx - tx) + abs(sy - ty)
        val += 0.15 * (best_move_dist - (abs(nx - tx) + abs(ny - ty)))

        cand = (val, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[1], best[2]]