def choose_move(observation):
    me = observation["self_position"]
    opp = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Select best resource for advantage: closer for me, farther for opponent
    best = None
    best_val = None
    for r in resources:
        if tuple(r) in obstacles:
            continue
        dv_me = cheb(me, r)
        dv_opp = cheb(opp, r)
        val = dv_me - 0.85 * dv_opp  # lower is better
        if best is None or val < best_val:
            best = r
            best_val = val

    if best is None:
        # No resources: drift toward center
        tx, ty = (grid_w - 1) / 2.0, (grid_h - 1) / 2.0
        best = [int(round(tx)), int(round(ty))]

    tx, ty = best[0], best[1]

    # Candidate moves
    options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = me[0] + dx, me[1] + dy
            if nx < 0 or ny < 0 or nx >= grid_w or ny >= grid_h:
                continue
            if (nx, ny) in obstacles:
                continue
            # Primary: move closer to target (chebyshev-like via squared euclid)
            d_new = cheb([nx, ny], [tx, ty])
            d_old = cheb(me, [tx, ty])
            # Secondary: slightly prefer increasing opponent distance to target
            d_opp_new = cheb(opp, [tx, ty])
            val = d_new - 0.05 * d_opp_new
            # Tertiary: prefer moves that don't step away from opponent (keeps pressure)
            val += 0.0001 * cheb([nx, ny], opp)
            # Penalize no-op if improvement is possible
            if dx == 0 and dy == 0 and d_new > d_old:
                val += 1.0
            options.append((val, dx, dy))

    if not options:
        return [0, 0]

    options.sort(key=lambda x: x[0])
    _, dx, dy = options[0]
    return [int(dx), int(dy)]