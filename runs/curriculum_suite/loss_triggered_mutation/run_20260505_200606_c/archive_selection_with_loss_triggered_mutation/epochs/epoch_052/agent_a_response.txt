def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (w - 1, h - 1) if sx < w - 1 else (0, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Prefer resources we can reach earlier than opponent; if none, head to reduce our distance to a good option.
    best = None
    for m in moves:
        dxm, dym = m
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate this move by best contested resource, plus small tie-breakers.
        best_adv = None
        best_res = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer than opponent
            key = (adv, -sd, -od, rx, ry)
            if best_res is None or key > best_res:
                best_res = key
            if best_adv is None or adv > best_adv:
                best_adv = adv

        # If we can beat someone, prioritize largest advantage; otherwise reduce our distance and lightly avoid moving toward blocked chokepoints.
        adv, nsd, nod, rx, ry = best_res
        # Lookahead: discourage stepping into being closer to opponent's nearest resource than we are (reduce accidental swaps).
        opp_best_d = None
        for r2x, r2y in resources:
            d2 = md(ox, oy, r2x, r2y)
            if opp_best_d is None or d2 < opp_best_d:
                opp_best_d = d2
        my_best_d = None
        for r2x, r2y in resources:
            d2 = md(nx, ny, r2x, r2y)
            if my_best_d is None or d2 < my_best_d:
                my_best_d = d2

        # Add deterministic obstacle-density penalty around our new position.
        neigh_blocks = 0
        for ax, ay in moves:
            ex, ey = nx + ax, ny + ay
            if not inb(ex, ey) or (ex, ey) in obstacles:
                neigh_blocks += 1
        score = (adv, -my_best_d, -neigh_blocks, -nod, -sd, -rx - ry)
        if best is None or score > best:
            best = score
            best_move = [dxm, dym]

    return best_move if best is not None else [0, 0]