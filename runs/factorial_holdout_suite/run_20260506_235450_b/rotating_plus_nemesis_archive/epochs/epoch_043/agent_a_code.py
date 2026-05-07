def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    turns_remaining = observation.get("turns_remaining", 0)

    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = {(r[0], r[1]) for r in resources}

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def nearest_from(x, y):
        best_d = 10**9
        best_r = None
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best_d or (d == best_d and (rx, ry) < best_r):
                best_d = d
                best_r = (rx, ry)
        return best_d, best_r

    # Determine a primary target: closest resource to us; tie-break by coordinates
    my_d0, target = nearest_from(sx, sy)
    tx, ty = target

    # If late game, prioritize any immediate resource over race
    late = turns_remaining <= 6

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        immediate = 1.0 if (nx, ny) in res_set else 0.0

        # Race term: prefer positions that reduce our distance to target relative to opponent
        my_dt = cheb(nx, ny, tx, ty)
        opp_dt = cheb(ox, oy, tx, ty)
        race = (opp_dt - my_dt)

        # Backup: if target is blocked by obstacles, allow moving toward nearest resource instead
        my_dn, _ = nearest_from(nx, ny)
        seek = -float(my_dn)

        # Small preference to avoid drifting away from target early
        toward = -0.15 * float(my_dt)

        val = 0.0
        if late:
            val = 10.0 * immediate + 1.2 * seek + toward
        else:
            val = 8.0 * immediate + 0.9 * race + 0.7 * seek + toward

        # Deterministic tie-break: prefer lexicographically smaller (dx,dy) among equal values
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]