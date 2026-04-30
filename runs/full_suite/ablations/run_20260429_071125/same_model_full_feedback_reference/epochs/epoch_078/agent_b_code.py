def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = None
        best_score = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            lead = d_op - d_me  # positive if we're closer
            # small tie-break to move away from our far-from-edge stagnation:
            edge_bias = (rx == 0 or rx == w - 1) + (ry == 0 or ry == h - 1)
            score = lead * 1000 - d_me * 3 + edge_bias
            if score > best_score:
                best_score = score
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w - 1) - sx, (h - 1) - sy  # deterministic fallback: head toward opposite-corner mirror

    # Choose move: primary = reduce our distance to target; secondary = disrupt opponent (increase their distance to our target).
    best_move = (0, 0)
    best_tuple = (-10**18, -10**18, -10**18)  # (improve, opp_dist, -step_index)

    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op_after = cheb(ox, oy, tx, ty)  # opponent assumed steady; we still prefer moves that get us closer faster
        # If standing still helps only when at target; otherwise avoid stagnation.
        improve = -d_me
        # Prefer being closer and also staying away from opponent when equally good on distance.
        dist_opp = cheb(nx, ny, ox, oy)
        t = (improve, d_op_after + dist_opp * 0.01, -(i))
        if t > best_tuple:
            best_tuple = t
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]