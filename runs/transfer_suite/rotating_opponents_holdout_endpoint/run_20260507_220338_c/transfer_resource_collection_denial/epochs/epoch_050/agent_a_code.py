def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    # If we're already on a resource, do nothing (deterministic collection).
    if (sx, sy) in set(resources):
        return [0, 0]

    # Predict opponent's likely target: closest for opponent with slight bias away from ours.
    best_op = None
    best_op_key = None
    for rx, ry in resources:
        od = cheb(ox, oy, rx, ry)
        sd = cheb(sx, sy, rx, ry)
        key = (od, -sd)  # minimize opponent distance; if tie, favor where we are farther
        if best_op_key is None or key < best_op_key:
            best_op_key = key
            best_op = (rx, ry)
    opp_tx, opp_ty = best_op

    # Choose our target based on time-to-reach advantage vs opponent.
    # Add small "diversion" term toward the opponent's predicted target to block races.
    best_me = None
    best_me_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        advantage = (opd - myd)  # positive is good for us
        block = -cheb(rx, ry, opp_tx, opp_ty)  # closer to their predicted target slightly preferred
        # Prefer strictly positive advantage; otherwise prefer least self time and better advantage.
        key = (0 if advantage > 0 else 1, -advantage, myd, block)
        if best_me_key is None or key < best_me_key:
            best_me_key = key
            best_me = (rx, ry)
    tx, ty = best_me

    # Move greedily toward target with deterministic tie-break while avoiding obstacles.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    curd = cheb(sx, sy, tx, ty)
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Tie-break: keep closer to target; avoid giving opponent immediate improvement (slightly).
        opp_nd = cheb(ox, oy, tx, ty)
        key = (0 if nd < curd else 1, nd, cheb(nx, ny, ox, oy), dx, dy, opp_nd)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]