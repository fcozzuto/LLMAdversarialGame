def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    oppx, oppy = ox, oy
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Choose the resource we would be best positioned to secure next.
        best_r = None
        best_adv = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(oppx, oppy, rx, ry)
            adv = od - sd  # positive: we are closer
            key = (-(adv), sd > od, sd, rx, ry)
            if best_adv is None or key < (-(best_adv),):
                best_r = (rx, ry)
                best_adv = adv
            # Use direct update for determinism
            if best_r is None or (-(adv), sd > od, sd, rx, ry) < (-(best_adv), man(nx, ny, best_r[0], best_r[1]) > man(oppx, oppy, best_r[0], best_r[1]), man(nx, ny, best_r[0], best_r[1]), best_r[0], best_r[1]):
                best_r = (rx, ry)
                best_adv = adv

        tx, ty = best_r
        self_d = man(nx, ny, tx, ty)
        opp_d = man(oppx, oppy, tx, ty)
        # Prefer securing advantage; then being faster to the chosen target; penalize allowing opponent to be close.
        val = best_adv * 1000 - self_d * 3 - opp_d
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]