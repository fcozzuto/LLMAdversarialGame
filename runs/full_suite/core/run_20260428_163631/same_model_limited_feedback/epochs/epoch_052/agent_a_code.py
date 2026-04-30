def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        best = None
        for rx, ry in sorted(resources):
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer targets we can reach relatively sooner than opponent
            val = d_me - 0.35 * d_op
            if best is None or val < best[0]:
                best = (val, rx, ry)
        _, tx, ty = best
    else:
        tx, ty = (w // 2), (h // 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            v = 10**9
        else:
            # Move closer to target; slight preference for cells closer to target than opponent
            my_d = cheb(nx, ny, tx, ty)
            op_d = cheb(ox, oy, tx, ty)
            v = my_d - 0.12 * op_d
            # Small tie-break: prefer moving (not staying) when not on target
            if (sx, sy) != (tx, ty) and (dx == 0 and dy == 0):
                v += 0.05
        if best_val is None or v < best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]