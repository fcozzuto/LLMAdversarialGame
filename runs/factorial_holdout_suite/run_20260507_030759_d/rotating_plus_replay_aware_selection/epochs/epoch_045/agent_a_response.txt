def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_val = -10**18
    best_sd = 10**18
    best_od = 10**18
    best_move = [0, 0]

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue

        move_best = -10**18
        move_best_sd = 10**18
        move_best_od = 10**18

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer

            # Prefer taking resources where we're closer; then prefer faster progress (smaller sd)
            # and reduce opponent's access (larger od).
            val = 1000 * adv - 3 * sd + od

            if val > move_best or (val == move_best and (sd < move_best_sd or (sd == move_best_sd and od < move_best_od))):
                move_best, move_best_sd, move_best_od = val, sd, od

        if move_best > best_val or (move_best == best_val and (move_best_sd < best_sd or (move_best_sd == best_sd and move_best_od < best_od))):
            best_val, best_sd, best_od = move_best, move_best_sd, move_best_od
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]