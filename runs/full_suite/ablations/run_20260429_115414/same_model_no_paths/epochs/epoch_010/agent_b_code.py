def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if r is not None]
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return x < 0 or y < 0 or x >= w or y >= h or (x, y) in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not blocked(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Select best target: prioritize resources we can reach well vs opponent.
    best_t = resources[0]
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # Encourage opponent to be further and our reach to be smaller.
        key = (op_d - my_d, -my_d, -op_d, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    my0 = cheb(sx, sy, tx, ty)
    op0 = cheb(ox, oy, tx, ty)

    # Evaluate moves.
    best_m = (0, 0)
    best_v = None
    for dx, dy, nx, ny in legal:
        my1 = cheb(nx, ny, tx, ty)
        op1 = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        gain_my = my0 - my1
        # Penalize moving into near-opponent to avoid being "contested" cells.
        opp_near = cheb(nx, ny, ox, oy)
        contest_pen = 2 if opp_near <= 1 else (1 if opp_near <= 2 else 0)
        # Small bonus if we land on a resource.
        pick_bonus = 6 if (nx, ny) in set(resources) else 0
        # If we are closer than opponent after moving, add extra push.
        my_vs_op = 3 if my1 < op0 else 0
        v = (gain_my * 5) + (my_vs_op * 4) - contest_pen + pick_bonus - (abs(nx - tx) + abs(ny - ty)) * 0.01
        if best_v is None or v > best_v or (v == best_v and (dx, dy) < best_m):
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]