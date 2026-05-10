def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    sr = str(observation.get("self_role") or "")
    ir_pursuer = ("pursur" in sr.lower()) or ("chaser" in sr.lower()) or ("hunter" in sr.lower())

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_pen(nx, ny):
        p = 0
        for bx, by in blocked:
            if abs(nx - bx) <= 0 and abs(ny - by) <= 0:
                return 10**6
            if abs(nx - bx) <= 1 and abs(ny - by) <= 1:
                p += 1
        return p

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best_key = None
    best_move = (0, 0)
    ti = int(observation.get("turn_index") or 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d = cheb(nx, ny, ox, oy)
        pen = adj_pen(nx, ny)
        # Evader: prefer far from opponent, then far from obstacles, then toward the best corner.
        # Pursuer: prefer close to opponent, then far from obstacles (to avoid getting jammed), then toward opponent’s corner-side.
        corner_bias = -cheb(nx, ny, tx, ty)  # larger is better for evader
        toward_corner = -corner_bias
        jitter = ((nx + 3 * ny + dx - 2 * dy + ti) & 3)

        if ir_pursuer:
            key = (d, pen, toward_corner, jitter)
        else:
            key = (-d, pen, corner_bias, jitter)

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]