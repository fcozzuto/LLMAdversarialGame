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

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        cand = []
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources we're strictly closer to; otherwise still go for nearest.
            bias = 0 if d_self <= d_opp else 1
            cand.append((bias, d_self, d_opp, rx + ry, rx, ry))
        _, _, _, _, tr_x, tr_y = sorted(cand)[0]
    else:
        tr_x = 3 if sx <= 3 else 4 if sx >= 4 else sx
        tr_y = 3 if sy <= 3 else 4 if sy >= 4 else sy

    best = None
    for dx, dy, nx, ny in legal:
        d = cheb(nx, ny, tr_x, tr_y)
        # Small deterministic tie-break: prefer staying or moving towards increasing x, then y.
        score = (d, 0 if (dx == 0 and dy == 0) else 1, -dx, -dy)
        if best is None or score < best[0]:
            best = (score, [dx, dy])
    return best[1]