def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        scored = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            best_r = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < best_r:
                    best_r = d
            best_o = cheb(nx, ny, ox, oy)
            # Prefer closer to resources; if tie, stay farther from opponent (helps secure).
            score = best_r * 1000 - best_o
            scored.append((score, dx, dy))
        if scored:
            scored.sort(key=lambda t: (t[0], t[1], t[2]))
            return [int(scored[0][1]), int(scored[0][2])]

    # No resources: go toward center while keeping distance from opponent.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        to_c = cheb(nx, ny, cx, cy)
        away_o = cheb(nx, ny, ox, oy)
        score = to_c * 1000 - away_o
        if best is None or score < best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]