def choose_move(observation):
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles_list = observation.get('obstacles', []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        v = ax - bx
        if v < 0:
            v = -v
        u = ay - by
        if u < 0:
            u = -u
        return v + u

    best = None  # (value, selfdist_bias, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by best resource target for this move: maximize "being closer than opponent"
        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Advantage primarily; also prefer shorter self distance for faster collection.
            val = (od - sd) * 1000 - sd
            cand = (val, sd)
            if best_for_move is None or cand > best_for_move:
                best_for_move = cand

        if best_for_move is None:
            continue
        value, sd_bias = best_for_move
        cand_best = (value, -sd_bias, dx, dy)  # invert for deterministic tie-breaking
        if best is None or cand_best > best:
            best = cand_best

    if best is None:
        return [0, 0]
    return [best[2], best[3]]