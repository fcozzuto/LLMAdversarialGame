def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a tactical target: prefer resources we can reach much earlier than opponent, and closer to center.
    if resources:
        best_r = None
        best_val = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Higher is better: big positive means we are closer than opponent.
            center_boost = -0.05 * (abs(rx - cx) + abs(ry - cy))
            val = (do - ds) + center_boost
            # Deterministic tie-break: closer to our position, then lexicographic.
            if val > best_val or (val == best_val and (ds < cheb(sx, sy, best_r[0], best_r[1]) if best_r else True)):
                best_val = val
                best_r = (rx, ry)
    else:
        best_r = (int(cx), int(cy))

    rx, ry = best_r
    best_move = (0, 0)
    best_score = -10**18

    # Evaluate each move: maximize (opponent distance - self distance) after the move.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        # Slightly prefer reducing absolute self distance and avoiding being stuck.
        score = (do2 - ds2) - 0.02 * ds2
        # Deterministic tie-break: smallest lexicographic move delta among equals.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]