def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Deny/escape if no resources visible
    if not resources:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best = None
        best_move = [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            t = cheb((nx, ny), (tx, ty))
            score = -t
            if best is None or score > best:
                best = score
                best_move = [dx, dy]
        return best_move

    # Precompute distances to resources from current positions
    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Lead to nearest resource considering opponent
        my_min = 10**9
        opp_min = 10**9
        my2_min = 10**9  # secondary to break ties toward clusters
        for rx, ry in resources:
            d_my = cheb((nx, ny), (rx, ry))
            d_opp = cheb((ox, oy), (rx, ry))
            if d_my < my_min:
                my2_min = my_min
                my_min = d_my
            elif d_my < my2_min:
                my2_min = d_my
            if d_opp < opp_min:
                opp_min = d_opp

        # Encourage immediate collection, then maximize lead (opponent distance minus ours),
        # and slightly favor moving toward denser/closer resource sets.
        # Use opp_min as a cheap opponent pressure signal.
        lead = opp_min - my_min
        score = 1000 * (1 if my_min == 0 else 0) + 10 * lead - my_min - 0.1 * my2_min

        # Small nudge: avoid moving closer to obstacles by using min obstacle distance
        if obstacles:
            mo = 10**9
            for ax, ay in obstacles:
                d_ob = cheb((nx, ny), (ax, ay))
                if d_ob < mo:
                    mo = d_ob
            score += 0.05 * mo

        if best is None or score > best:
            best = score
            best_move = [dx, dy]
    return best_move