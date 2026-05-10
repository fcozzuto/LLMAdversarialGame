def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    if not resources:
        return [0, 0]

    # Select resource we can likely arrive at first (deterministic scoring).
    best = None
    bx = by = 0
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer: close for us, far for opponent; penalize our behind-ness strongly.
        score = ds - 0.9 * do
        # Mild tie-break to avoid wall hugging: prefer cells with more nearby freedom.
        score2 = score - 0.02 * free_neighbors(rx, ry)
        if best is None or score2 < best:
            best = score2
            bx, by = rx, ry

    # If all resources are invalid (e.g., all in obstacles), stay.
    if best is None:
        return [0, 0]

    # Choose a single-step move minimizing time to target, avoiding obstacles, with stability tie-break.
    best_move = (0, 0)
    best_rank = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        t = cheb(nx, ny, bx, by)
        # Encourage staying if equally good, and discourage moves that reduce local freedom.
        nf = free_neighbors(nx, ny)
        rank = (t, -nf, abs(dx) + abs(dy), dx, dy)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]