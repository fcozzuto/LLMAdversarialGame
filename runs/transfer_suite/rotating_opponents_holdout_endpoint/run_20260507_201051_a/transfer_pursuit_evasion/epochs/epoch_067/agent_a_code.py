def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    resources = observation.get("resources") or []
    my_evade = False
    sr = (observation.get("self_role") or "").lower()
    orr = (observation.get("opponent_role") or "").lower()
    if "evad" in sr or "escape" in sr or "runner" in sr:
        my_evade = True
    if "purs" in sr:
        my_evade = False
    if "purs" in orr:
        my_evade = ("evad" in sr or "evader" in sr or "escape" in sr or "runner" in sr)

    tx, ty = None, None
    if isinstance(resources, list) and resources:
        bestd = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                x, y = int(r[0]), int(r[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    d = cheb(sx, sy, x, y)
                    if bestd is None or d < bestd:
                        bestd = d
                        tx, ty = x, y
    if tx is None:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        d_r = cheb(nx, ny, sx, sy)
        avoid = d_t + (0 if my_evade else 0)
        if my_evade and tx == ox and d_o <= cheb(sx, sy, ox, oy):
            val = 1000 + d_o
        else:
            val = -d_t + (0 if my_evade else 0) - 0.01 * d_r
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if not valid(sx + dx, sy + dy):
        return [0, 0]
    return [dx, dy]