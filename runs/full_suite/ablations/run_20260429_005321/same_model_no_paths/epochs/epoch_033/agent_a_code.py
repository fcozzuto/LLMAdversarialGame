def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx = (w - 1) if sx <= (w - 1) // 2 else 0
        ty = (h - 1) if sy <= (h - 1) // 2 else 0
    else:
        best_t = None
        best_v = -10**18
        for (rx, ry) in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we arrive earlier than the opponent, otherwise still head to the best contest.
            v = (do - ds) * 1000 - ds
            if v > best_v or (v == best_v and (rx, ry) < best_t):
                best_v = v
                best_t = (rx, ry)
        tx, ty = best_t

    if (sx, sy) == (tx, ty):
        tx2, ty2 = (0 if tx > (w - 1) // 2 else w - 1), (0 if ty > (h - 1) // 2 else h - 1)
        tx, ty = tx2, ty2

    best_move = (0, 0)
    best_cost = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        cost = cheb(nx, ny, tx, ty) * 10 - cheb(nx, ny, ox, oy)
        if cost < best_cost or (cost == best_cost and (dx, dy) < best_move):
            best_cost = cost
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]