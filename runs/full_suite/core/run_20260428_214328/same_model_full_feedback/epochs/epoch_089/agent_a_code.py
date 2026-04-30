def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # No resources visible: drift toward center while avoiding obstacles.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_step = (0, 0)
        best_d = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d = cheb(nx, ny, cx, cy)
                if d < best_d:
                    best_d = d
                    best_step = (dx, dy)
        return [best_step[0], best_step[1]]

    # Pick a resource where we are ahead (or least behind) in time.
    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Reward leading and penalize being far; tie-break by absolute distance.
        val = (d_op - d_me) * 1000 - d_me
        if val > best_val or (val == best_val and (d_me < cheb(sx, sy, best_t[0], best_t[1]) if best_t else True)):
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t

    # Choose the move that reduces our distance to the target most.
    best_step = (0, 0)
    best_pair = None  # (d_after, d_opp_after)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_after = cheb(nx, ny, tx, ty)
        d_op_after = cheb(ox, oy, tx, ty)
        pair = (d_after, -d_op_after)
        if best_pair is None or pair < best_pair:
            best_pair = pair
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]