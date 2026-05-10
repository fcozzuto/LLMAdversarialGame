def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose target deterministically: good for us while discouraging the opponent.
    best_t = None
    best_t_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # prioritize resources we can reach first; add small bias to closer ones
        key = (ds - do, ds + 0.01 * (rx + ry))
        if best_t_key is None or key < best_t_key:
            best_t_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # Also note resources near opponent for interception/denial
    near_opp = []
    for rx, ry in resources:
        if man(ox, oy, rx, ry) <= 2:
            near_opp.append((rx, ry))

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Primary: reduce distance to chosen target
        ds_t = man(nx, ny, tx, ty)
        val = -ds_t

        # Secondary: if we're adjacent to a near-opponent resource, prioritize it more
        if near_opp:
            ds_no = None
            for rx, ry in near_opp:
                d = man(nx, ny, rx, ry)
                if ds_no is None or d < ds_no:
                    ds_no = d
            val += -0.9 * ds_no

            # Denial: attempt to move toward those contested cells (reduces opponent capture pressure)
            # by increasing opponent distance to the closest contested cell.
            best_do = None
            for rx, ry in near_opp:
                d = man(ox, oy, rx, ry)
                if best_do is None or d < best_do:
                    best_do = d
            # if we can reach a contested cell sooner, it matters; approximate via ds_no - best_do
            if ds_no is not None:
                val += -0.3 * (ds_no - best_do)

        # Small tie-break: prefer moves that reduce our distance to opponent (intercept posture)
        val += -0.05 * man(nx, ny, ox, oy)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]