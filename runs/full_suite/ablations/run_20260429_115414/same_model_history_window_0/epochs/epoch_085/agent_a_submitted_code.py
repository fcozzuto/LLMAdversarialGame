def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation["grid_width"]
    gh = observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    res = observation.get("resources", [])
    obs_set = set(obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh:
            return False
        return (nx, ny) not in obs_set

    def man(p, q):
        return abs(p[0] - q[0]) + abs(p[1] - q[1])

    my_pos = (x, y)
    opp_pos = (ox, oy)

    if res:
        # Pick a resource where we're relatively closer; tie-break lexicographically.
        best_t = None
        best_key = None
        for r in res:
            dmy = man(r, my_pos)
            dop = man(r, opp_pos)
            key = (-(dop - dmy), r[0], r[1])  # smaller is better
            if best_key is None or key < best_key:
                best_key = key
                best_t = r
        tx, ty = best_t
    else:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not legal(nx, ny):
            continue
        myd = abs(nx - tx) + abs(ny - ty)
        opd = abs(nx - ox) + abs(ny - oy)
        # Prefer smaller distance to target, larger opponent distance.
        val = (myd, -opd, abs(nx - (gw - 1) / 2) + abs(ny - (gh - 1) / 2), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]