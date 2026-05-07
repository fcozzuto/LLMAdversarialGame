def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    best_move = (0, 0)
    best_val = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Margin: how much closer we are to a resource than opponent
        best_margin = None
        best_selfd = None
        for (rx, ry) in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd
            if best_margin is None or margin > best_margin or (margin == best_margin and sd < best_selfd):
                best_margin = margin
                best_selfd = sd
        # If opponent is closer everywhere (margin <= 0), also try to increase distance from opponent a bit
        opp_d = cheb(nx, ny, ox, oy)
        val = (best_margin, -best_selfd, opp_d)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]