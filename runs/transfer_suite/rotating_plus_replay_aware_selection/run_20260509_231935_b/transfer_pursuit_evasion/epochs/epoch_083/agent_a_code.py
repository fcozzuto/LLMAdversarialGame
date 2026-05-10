def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_cell(nx, ny):
        d = cheb(nx, ny, ox, oy)
        if pursuer:
            return -d * 100 - abs(nx - ox) - abs(ny - oy)
        else:
            return d * 100 + abs(nx - ox) + abs(ny - oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None
    # Deterministic tie-break: prefer moves in this fixed order if equal score.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = score_cell(nx, ny)

        # Extra shaping: discourage hugging obstacles by penalizing if next to any obstacle.
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_pen += 1
        if pursuer:
            v -= adj_pen * 2
        else:
            v += adj_pen * (-2)

        if best is None or v > bestv:
            best = (dx, dy)
            bestv = v

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]