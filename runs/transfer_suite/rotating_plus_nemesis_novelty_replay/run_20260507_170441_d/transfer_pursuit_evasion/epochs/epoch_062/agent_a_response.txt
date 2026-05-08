def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    role = (observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda p: cheb(p[0], p[1], ox, oy))
        best_key = None
        best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            md = cheb(nx, ny, tx, ty)
            key = (d, mobility(nx, ny), -md, -dx, -dy)
            if best_key is None or key > best_key:
                best_key, best = key, (dx, dy)
        return [int(best[0]), int(best[1])]

    # pursuer
    best_key = None
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        key = (-d, mobility(nx, ny), nx, ny, -dx, -dy)
        if best_key is None or key > best_key:
            best_key, best = key, (dx, dy)
    return [int(best[0]), int(best[1])]