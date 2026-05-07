def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None  # (primary, tie1, tie2, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate best target from this next position
        best_adv = -10**9
        best_selfd = 10**9
        best_opd = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # higher is better
            # primary: maximize advantage; tie: smaller our distance; tie: smaller opponent distance
            if adv > best_adv or (adv == best_adv and (sd < best_selfd or (sd == best_selfd and od < best_opd))):
                best_adv, best_selfd, best_opd = adv, sd, od

        # Primary goal: pick move that maximizes achievable advantage.
        # If no positive advantage anywhere, still choose move minimizing our distance to the best (least-bad) target.
        primary = best_adv
        tie1 = best_selfd
        tie2 = best_opd
        cand = (primary, tie1, tie2, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[3], best[4]]