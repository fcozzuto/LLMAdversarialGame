def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = {(int(a), int(b)) for a, b in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            if free(x + dx, y + dy):
                c += 1
        return c

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if nx == ox and ny == oy:  # capture if pursuer; avoid if we're evader
            if is_evader:
                continue
        d = cheb(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)

        # Obstacle-aware: prefer moves not hugging obstacles too tightly (use nearest obstacle manhattan).
        mind = 999
        for ax, ay in obs:
            md = man(nx, ny, ax, ay)
            if md < mind:
                mind = md
                if mind <= 1:
                    break

        if is_evader:
            # Run away from zigzags: prioritize distance, then avoid dead-ends, then avoid tight obstacle proximity.
            score = (d * 100) + (fn * 3) + (mind * 1)
        else:
            # Pursue: prioritize reducing chebyshev distance, then increase mobility, then keep some separation from obstacles.
            score = (-d * 100) + (fn * 2) + (mind * 0.5)

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]