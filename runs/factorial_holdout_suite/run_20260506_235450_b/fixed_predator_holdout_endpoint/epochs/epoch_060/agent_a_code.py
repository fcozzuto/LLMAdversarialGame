def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is None:
            continue
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Opportunistic denial:
    # Prefer resources where we can arrive no later than opponent; otherwise race the best "beat" candidate.
    # Add small penalty for moving toward walls/obstacle cells to avoid boundary-locking.
    def cell_pen(nx, ny):
        pen = 0
        if nx == 0 or nx == w - 1: pen += 0.2
        if ny == 0 or ny == h - 1: pen += 0.2
        if (nx, ny) in obstacles: pen += 1000
        return pen

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue

        # Look at top few resource candidates based on opponent proximity (deterministic).
        # This focuses on denying the pool rather than wandering.
        res_sorted = sorted(resources, key=lambda r: (cheb(r[0], r[1], ox, oy), cheb(r[0], r[1], sx, sy), r[0], r[1]))
        score = 0.0
        for i, r in enumerate(res_sorted[:4]):
            rx, ry = r[0], r[1]
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # If we can get there first or tie, strongly reward; else reward reducing the gap.
            gap = d_opp - d_self
            arrive_bonus = 0
            if d_self <= d_opp:
                arrive_bonus = 10.0 - d_self
            score += (gap * 2.0 + arrive_bonus) * (1.0 / (1 + i))
        score -= cell_pen(nx, ny)

        # Tie-break: closer to center and deterministic by (nx, ny)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= 0.01 * (abs(nx - cx) + abs(ny - cy))

        if best_score is None or score > best_score or (score == best_score and (nx, ny) < (best_move[0] + sx, best_move[1] + sy)):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]