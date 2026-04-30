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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas = sorted(deltas)

    if resources:
        best = None
        for rx, ry in resources:
            dm = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Materially different from "closest resource": focus on winning the race to a resource.
            # Large positive => I'm significantly closer.
            val = (do - dm) * 100 - dm
            if best is None or val > best[0]:
                best = (val, rx, ry)
        _, tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Greedy local step toward target, but refuse to step into an obviously losing approach.
    cur_me_d = cheb(sx, sy, tx, ty)
    cur_op_d = cheb(ox, oy, tx, ty)
    best_move = (None, -10**9)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nm = cheb(nx, ny, tx, ty)
        # Increase the race advantage; also prefer getting closer to resources generally.
        nm_op = cheb(ox, oy, tx, ty)
        adv = (nm_op - nm) * 100 - nm
        # If race advantage isn't improving, slightly prioritize avoiding the opponent.
        evade = cheb(nx, ny, ox, oy)
        score = adv + (evade * 3) - (abs(nm - cur_me_d) * 1) - (abs(cur_op_d - nm_op) * 0)
        if score > best_move[1]:
            best_move = ((dx, dy), score)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]