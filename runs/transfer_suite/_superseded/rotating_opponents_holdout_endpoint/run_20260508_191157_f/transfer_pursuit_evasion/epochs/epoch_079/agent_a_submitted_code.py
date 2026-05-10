def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    pursuer = (observation.get("self_role", "pursuer") != "evader")

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy
    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                c += 1
        return c
    def corner_options(px, py):
        xs = 0 if px < w - 1 - px else w - 1
        ys = 0 if py < h - 1 - py else h - 1
        return [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)], (xs, ys)

    corners, approx_corner = corner_options(ox, oy)
    # For pursuer: choose corner that opponent is "more likely" aiming at, then go for that cutoff.
    # For evader: choose the opposite corner from pursuer.
    if pursuer:
        tx, ty = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        # Make it harder for zigzag evasion by aiming near the opponent-to-wall direction.
        wall_dir = (0 if ox < w - 1 else w - 1, 0 if oy < h - 1 else h - 1)
        tx2, ty2 = approx_corner
    else:
        tx, ty = min(corners, key=lambda c: dist2(c[0], c[1], sx, sy))
        tx2, ty2 = max(corners, key=lambda c: dist2(c[0], c[1], sx, sy))
        wall_dir = None

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        if pursuer and nx == ox and ny == oy:
            return [dx, dy]

        dO = dist2(nx, ny, ox, oy)
        # Avoid stepping into tight spots (zigzag tends to exploit funnels).
        fn = free_neighbors(nx, ny)
        tight_pen = (2 - fn) if fn < 2 else 0

        # Corner-cut: for pursuer chase toward opponent's likely escape corner; for evader flee away.
        dC = dist2(nx, ny, tx, ty)
        dC2 = dist2(nx, ny, tx2, ty2)

        # Also prefer maintaining a "block" position near the segment between pursuer and target.
        if pursuer:
            block_x = tx
            block_y = ty
            dBlock = dist2(nx, ny, block_x, block_y)
            score = -dO * 2.0 - d