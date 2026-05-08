def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def edge_proximity(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_score = None
    best_move = (0, 0)

    if pursuer:
        # Chase with slight preference for staying off obstacles' "shadow" by steering toward edges (reduce escape area).
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            edge = edge_proximity(nx, ny)  # closer to edge => smaller
            # Lower d is good, higher score = better
            score = -d - 0.05 * edge
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Evader: maximize separation; also avoid giving pursuer easy row/col alignment; steer toward edge to limit pursuer routes.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)
        off_center = dist2(nx, ny, cx, cy)
        penalty_align = 0
        if nx == ox or ny == oy:
            penalty_align += 6.0
        # Prefer being closer to edges (harder to zigzag around obstacles) but not hugging center.
        score = 1.0 * d2 + 0.35 * man - 0.02 * off_center - penalty_align - 0.01 * edge_proximity(nx, ny)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]