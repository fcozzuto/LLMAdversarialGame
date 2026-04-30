def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    # Target resources that opponent is unlikely to reach sooner; otherwise steer to a safer corner.
    if resources:
        best_r = None
        best_val = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer closer-than-opponent; discourage ties where opponent is competitive.
            val = d_me - 0.9 * d_op + (0.15 * (d_me == d_op))
            if best_val is None or val < best_val or (val == best_val and (rx + ry) < (best_r[0] + best_r[1])):
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # If no visible resources, move to the corner farther from opponent (avoid being trapped).
        if (cheb(sx, sy, 0, h - 1) + cheb(sx, sy, w - 1, 0)) == 0:
            tx, ty = sx, sy
        else:
            c1 = cheb(ox, oy, 0, h - 1)
            c2 = cheb(ox, oy, w - 1, 0)
            tx, ty = (w - 1, 0) if c2 >= c1 else (0, h - 1)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_to_t = cheb(nx, ny, tx, ty)
        d_me_now = cheb(sx, sy, tx, ty)
        # Predict tactical pressure: prefer reducing distance to target and increasing distance from opponent.
        d_op_next = cheb(nx, ny, ox, oy)
        d_op_now = cheb(sx, sy, ox, oy)

        # If moving reduces our target distance, reward; if opponent gets much closer, penalize.
        delta_target = d_to_t - d_me_now
        delta_opp = d_op_next - d_op_now

        score = (d_to_t * 1.0) + (0.25 * delta_target) - (0.35 * delta_opp)

        # Deterministic tie-break: prefer (0,0) last? keep stable ordering from moves list.
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]