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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx = 1 if sx < (w - 1) // 2 else -1 if sx > (w - 1) // 2 else 0
        ty = 1 if sy < (h - 1) // 2 else -1 if sy > (h - 1) // 2 else 0
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if inb(nx, ny) and mx == tx and my == ty:
                return [mx, my]
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if inb(nx, ny):
                return [mx, my]
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        closest = None
        best_d = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < best_d:
                best_d = d
                closest = (rx, ry)
        rx, ry = closest
        opp_d = cheb(ox, oy, rx, ry)
        # Prefer smaller your distance; break ties by larger opponent distance.
        score = -best_d * 100 + opp_d
        # Small bias toward moving closer to opponent's side when equally good.
        score += (cheb(nx, ny, w - 1, h - 1) - cheb(sx, sy, w - 1, h - 1)) * 0.01
        if score > best_score:
            best_score = score
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]