def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    R = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                R.append((x, y))
    if not R:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    turn = int(observation.get("turn_index") or 0)
    total = int(observation.get("turns_remaining") or 0)
    urgency = 1.0 if total <= 6 else (0.6 if total <= 16 else 0.35)

    best_val = None
    best_move = (0, 0)
    for dx, dy, nx, ny in cand:
        # Bias toward resources on our side (opponent starts opposite corner)
        side_bias = (nx - ox) * 0.001 + (ny - oy) * 0.001
        v = -10**9
        for tx, ty in R:
            # Prefer stealing windows: maximize (opp_dist - self_dist)
            md = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            steal = od - md
            at_res = 1.0 if (nx == tx and ny == ty) else 0.0
            # If we are substantially behind, de-prioritize (resource_denier)
            behind_pen = 0.0 if steal >= 0 else (steal * steal) * (1.6 + urgency)
            # Small preference for closer targets to finish efficiently
            closeness = -0.05 * md
            val = (2.0 * steal) + (8.0 * at_res) + closeness - behind_pen + side_bias
            if val > v:
                v = val
        # Deterministic tie-break: smallest dx, then smallest dy, then closer
        if best_val is None or v > best_val + 1e-12:
            best_val = v
            best_move = (dx, dy)
        elif abs(v - best_val) <= 1e-12:
            bd, by = best_move
            if (dx, dy) < (bd, by):
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]