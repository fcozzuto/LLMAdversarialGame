def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # If no resources, head to the opponent corner (deterministic pressure).
    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb((nx, ny), (tx, ty))
            val = d
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Target by "advantage": resource where opponent is not significantly closer than us.
    # Then choose the move minimizing (our distance) while breaking ties by preserving advantage.
    best_target = resources[0]
    best_adv = None  # higher is better
    for r in resources:
        d_self = cheb((sx, sy), r)
        d_opp = cheb((ox, oy), r)
        adv = (d_opp - d_self)  # positive => we are closer
        if best_adv is None or adv > best_adv or (adv == best_adv and d_self < cheb((sx, sy), best_target)):
            best_adv = adv
            best_target = r

    tx, ty = best_target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self_next = cheb((nx, ny), (tx, ty))
        # Predict opponent not moving toward target: estimate their distance next as current-1 (optimistic).
        d_opp_now = cheb((ox, oy), (tx, ty))
        d_opp_next_est = max(0, d_opp_now - 1)
        adv_next = d_opp_next_est - d_self_next  # keep this high
        # Heuristic: primarily minimize self distance; second maximize advantage; third avoid moving away from opponent.
        val = (d_self_next, -adv_next, cheb((nx, ny), (ox, oy)))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]