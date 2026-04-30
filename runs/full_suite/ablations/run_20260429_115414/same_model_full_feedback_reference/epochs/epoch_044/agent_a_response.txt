def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    on_res = False
    for rx, ry in resources:
        if rx == sx and ry == sy:
            on_res = True
            break
    if on_res:
        return [0, 0]

    tx, ty = W // 2, H // 2
    best = None
    for rx, ry in resources:
        d_us = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        if best is None or (d_us - 0.6 * d_op, d_us, -rx, -ry) < best:
            best = (d_us - 0.6 * d_op, d_us, -rx, -ry)
            tx, ty = rx, ry

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        d2 = cheb(nx, ny, ox, oy)
        # Strongly prefer moves that reduce distance to target; slightly discourage approaching opponent too much.
        val = (d1, -d2)
        # If move lands on a resource, prioritize it.
        if (nx, ny) in resources:
            val = (0, -d2 - 1000)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]