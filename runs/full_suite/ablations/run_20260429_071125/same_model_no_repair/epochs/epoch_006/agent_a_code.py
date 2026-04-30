def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    occ = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in occ:
                continue
            v = -((nx - cx) ** 2 + (ny - cy) ** 2) - 0.1 * man((nx, ny), (ox, oy))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    res_list = [(r[0], r[1]) for r in resources]
    res_set = set(res_list)

    # Choose a target resource where we are at least as fast as opponent; otherwise pick the most winnable.
    best_target = None
    best_tv = -10**18
    for rx, ry in res_list:
        ds = man((sx, sy), (rx, ry))
        do = man((ox, oy), (rx, ry))
        # Large preference to resources we can reach earlier; smaller bias to central, and to those farther from opponent (harder to steal).
        tv = (do - ds) * 1000 - ds * 2 + (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * (-3)
        # Deterministic tie-break by coordinates
        tv += -(abs(rx - sx) + abs(ry - sy)) * 0.01
        if tv > best_tv or (tv == best_tv and (rx, ry) < best_target):
            best_tv = tv
            best_target = (rx, ry)

    tx, ty = best_target

    # Evaluate immediate move: collect if on resource, otherwise improve distance to target and deny opponent by increasing their distance to that target.
    best_move = (0, 0)
    best_sv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in occ:
            continue
        if (nx, ny) == (ox, oy):
            continue

        if (nx, ny) in res_set:
            sv = 10**9
        else:
            d_now = man((sx, sy), (tx, ty))
            d_after = man((nx, ny), (tx, ty))
            improve = d_now - d_after

            do_now = man((ox, oy), (tx, ty))
            do_after = do_now + 1  # slight belief we "pull ahead" next turn when we move toward target

            # Also discourage moves that let opponent become much closer by moving opposite direction from their position.
            opp_d = man((nx, ny), (ox, oy))
            sv = 2000 * improve + 8 * (d_after <= d_now) - 2 * (d_after - do_now) + 0.03 * opp_d + (do_after - do_now) * 5
            # Tiny deterministic tie-break favoring smaller coordinates of move
            sv += -0.001 * (nx * 0.1 + ny * 0.01)

        if sv > best_sv or (sv == best_sv and (dx, dy) < best_move):
            best_sv = sv
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]