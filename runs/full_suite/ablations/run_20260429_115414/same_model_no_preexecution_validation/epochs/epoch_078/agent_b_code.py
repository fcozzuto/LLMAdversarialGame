def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        def cheb(ax, ay, bx, by):
            dx = ax - bx
            if dx < 0: dx = -dx
            dy = ay - by
            if dy < 0: dy = -dy
            return dx if dx > dy else dy

        ox, oy = int(op[0]), int(op[1])
        best = None
        best_val = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            val = (d_me - 0.6 * d_op) + 0.02 * (abs(rx - (w - 1)) + abs(ry - (h - 1)))
            if best_val is None or val < best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    ox, oy = int(op[0]), int(op[1])
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # primary: reduce distance to target
        d_next = cheb(nx, ny, tx, ty)
        # secondary: don't let opponent gain too much on same target
        d_op_next = cheb(ox, oy, tx, ty)
        # tertiary: avoid getting too close to opponent (some blocking)
        block = cheb(nx, ny, ox, oy)
        score = d_next - 0.3 * d_op_next - 0.05 * block
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move