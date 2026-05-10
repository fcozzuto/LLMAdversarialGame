def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res_set = set((r[0], r[1]) for r in resources)

    best = None
    best_val = -10**18

    # Deterministic evaluation: prefer immediate pickup, then resources we can reach sooner than opponent,
    # with extra weight to deny opponent (minimize (opp_self_gap) while keeping self distance small).
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in res_set:
            immediate = 10**9
        else:
            immediate = 0

        # compute best target value for this landing cell
        cell_best = -10**18
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                continue
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Want sd < od; also keep sd small.
            # If opponent closer (od < sd), heavily penalize to avoid stepping into their sweep.
            gap = od - sd
            val = (gap * 2000) - (sd * 3) + (od * -0.5)
            # Slight bias toward resources nearer to our current position for determinism
            val += -((abs(nx - sx) + abs(ny - sy)) * 0.1)
            if val > cell_best:
                cell_best = val

        total = immediate + cell_best
        # tie-break deterministically by choosing move closest to opponent-corner direction (toward our best target)
        if best is None or total > best_val:
            best_val = total
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]