def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    # If no resources known, drift to the safer center while increasing distance from opponent a bit
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            score = -cheb(nx, ny, cx, cy) - 0.15 * cheb(nx, ny, ox, oy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Target resources that we can reach first, while being simultaneously "hard" for opponent to also reach
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        # Small obstacle penalty: discourage moving adjacent to obstacles if alternatives exist
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1

        move_best = -10**9
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Encourage being closer than opponent and overall closeness
            # (Opponent term mildly higher to reduce direct contention)
            score = (-1.2 * d_me) + (0.55 * d_op) - 0.02 * (d_me - d_op)
            if score > move_best:
                move_best = score

        # Additional shaping: don't run straight into the opponent unless it helps resource competition
        score_move = move_best - 0.08 * cheb(nx, ny, ox, oy) - 0.05 * adj_obs
        if best is None or score_move > best[0]:
            best = (score_move, dx, dy)

    return [best[1], best[2]]