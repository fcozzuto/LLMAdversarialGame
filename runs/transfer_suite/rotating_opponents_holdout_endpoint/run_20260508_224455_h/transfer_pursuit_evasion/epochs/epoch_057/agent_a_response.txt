def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "pursuer").lower()

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if role == "evader":
        best = None
        bestd = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    def legal_from(x, y):
        res = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                res.append((dx, dy, nx, ny))
        return res

    opp_legal = legal_from(ox, oy)
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, ox, oy)

        # Opponent-escape estimate: count moves that likely increase distance from our new position.
        escape = 0
        for _, _, px, py in opp_legal:
            if cheb(px, py, nx, ny) > dist:
                escape += 1

        # Tie-breaker: avoid adjacency to obstacles (less likely to get cornered), but prefer progress.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj += 1

        # Aim to reduce dist strongly; penalize giving opponent many escape moves; lightly penalize obstacles near us.
        val = (-dist * 100) - (escape * 8) - (adj * 0.5)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]