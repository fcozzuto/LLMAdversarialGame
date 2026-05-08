def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2 and inb(p[0], p[1]):
            unclaimed.append((p[0], p[1]))

    # Candidate move destinations (8-neighborhood + stay)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Pick a deterministic strategic target
    target = None
    best_t = None
    if unclaimed:
        # Prefer cells we can reach sooner than opponent; break ties by closer to us, then coordinates
        for x, y in unclaimed:
            dS = abs(x - sx) + abs(y - sy)
            dO = abs(x - ox) + abs(y - oy)
            # Higher is better: advantage = (dO - dS)
            key = (- (dO - dS), dS, dO, x, y)
            if best_t is None or key < best_t:
                best_t = key
                target = (x, y)
    else:
        # No unclaimed: chase opponent territory (allow flipping on entry)
        oppt = []
        for p in (observation.get("opponent_territory") or []):
            if p and len(p) >= 2 and inb(p[0], p[1]):
                oppt.append((p[0], p[1]))
        if oppt:
            for x, y in oppt:
                key = (md((sx, sy), (x, y)), md((ox, oy), (x, y)), x, y)
                if best_t is None or key < best_t:
                    best_t = key
                    target = (x, y)
        else:
            # Fallback to center
            target = (w // 2, h // 2)

    # Choose move that best advances toward target, while slightly discouraging giving opponent advantage
    best_m = None
    best_dxdy = (0, 0)
    for dx, dy, nx, ny in moves:
        dS = abs(nx - target[0]) + abs(ny - target[1])
        dO = abs(nx - ox) + abs(ny - oy)
        # Combine: primarily minimize distance to target; then prefer to increase opponent distance
        key = (dS, dO, abs(nx - sx) + abs(ny - sy), dx, dy)
        if best_m is None or key < best_m:
            best_m = key
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]