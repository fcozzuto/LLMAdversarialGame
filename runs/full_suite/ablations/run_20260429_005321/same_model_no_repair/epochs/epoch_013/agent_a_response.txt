def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def count_block_adj(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in obs:
                c += 1
        return c

    # Select target: prefer resources we can reach no worse than opponent; if none, prefer resources we reach best.
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # ahead>0 means we are closer or tie (do - ds)
            ahead = do - ds
            key = (-ahead, ds, count_block_adj(rx, ry), rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1, h - 1)

    # Choose move that improves our progress to target, and if opponent is also racing, keeps their distance large.
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # If we are not the closer racer, prioritize moves that increase our lead margin.
        lead = do2 - ds2
        key = (-lead, ds2, -do2, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]