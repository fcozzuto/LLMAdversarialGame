def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target_from(px, py):
        best = None
        best_adv = None
        best_d = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if best is None or adv > best_adv or (adv == best_adv and myd < best_d) or (adv == best_adv and myd == best_d and (rx, ry) < best):
                best = (rx, ry)
                best_adv = adv
                best_d = myd
        return best, best_adv, best_d

    target, _, _ = best_target_from(sx, sy)
    if target is None:
        return [0, 0]
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    best_myd = None

    opd0 = cheb(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        myd = cheb(nx, ny, tx, ty)
        adv = opd0 - myd

        # Small tie-break innovation: parity-dependent preference among equals
        parity = (observation.get("turn_index", 0) & 1)
        pref = 0
        if adv == (best_val if best_val is not None else None) and myd == best_myd:
            pref = ((dx + 2 * dy + parity) & 1)

        val = (adv, -myd, -pref)  # maximize adv, minimize myd
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
            best_myd = myd

    dx, dy = best_move
    return [int(dx), int(dy)]