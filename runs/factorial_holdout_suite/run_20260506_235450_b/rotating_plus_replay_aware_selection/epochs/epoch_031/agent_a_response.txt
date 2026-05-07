def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Prefer resources we can reach strictly before opponent; otherwise reduce contest.
    best_move = None
    best_key = None
    for dx, dy, nx, ny in legal:
        # Compute best target value for this move.
        move_best = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are earlier
            # Key: maximize lead, then minimize our distance, then prefer lower opponent distance.
            key = (lead, -ds, -do, rx, ry)
            if move_best is None or key > move_best[0]:
                move_best = (key, ds, do)
        key, ds, do = move_best
        # Additional: if we can secure something, strongly prefer that.
        secure_flag = 1 if ds < do else 0
        composite = (secure_flag, key[0], key[1], -key[2], key[3], key[4], dx, dy)
        if best_key is None or composite > best_key:
            best_key = composite
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]