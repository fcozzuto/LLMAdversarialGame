def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_t = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # want large (we are closer)
        intercept_bonus = 2.0 if ry == oy else 0.0  # sweep_rows: deny on opponent's row
        row_pressure = -0.1 * abs(ry - oy)       # prefer rows nearer their focus
        # small tie-break: prefer not too far from us to ensure progress
        key = (adv + intercept_bonus + row_pressure, -sd)
        if best is None or key > best:
            best = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal doesn't help and opponent is strictly closer, try a more direct step
    if dx != 0 and dy != 0:
        sd_diag = cheb(sx + dx, sy + dy, tx, ty)
        sd_l = cheb(sx + dx, sy, tx, ty)
        sd_u = cheb(sx, sy + dy, tx, ty)
        if sd_diag > sd_l and sd_l <= sd_u:
            dy = 0
        elif sd_diag > sd_u and sd_u < sd_l:
            dx = 0

    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]