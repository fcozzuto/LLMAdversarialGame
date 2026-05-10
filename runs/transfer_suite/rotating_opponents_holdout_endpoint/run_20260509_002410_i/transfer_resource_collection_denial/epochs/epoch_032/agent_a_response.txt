def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", [0, 0])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # If we can collect immediately, do it.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in set(resources):
            return [dx, dy]

    best_move = [0, 0]
    best_score = -10**9

    res_set = set(resources)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Choose target resource that we would most likely secure soon.
        # Score favors: closeness to our target, and opponent being farther from it.
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            if (rx, ry) in res_set:
                dm = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                # Also prefer resources closer than opponent by a margin
                if dm < my_best or (dm == my_best and do < opp_best):
                    my_best = dm
                    opp_best = do
        # Convert to a compact deterministic score
        score = (-my_best) + (opp_best - my_best) * 0.75
        # Slightly prefer moving in the direction that reduces total Manhattan to resources cluster
        score += -0.01 * min(man(nx, ny, rx, ry) for rx, ry in resources)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]