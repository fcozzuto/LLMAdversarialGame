def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]
    w = observation["grid_width"]
    h = observation["grid_height"]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = abs(rx - sx) + abs(ry - sy)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]
        cx, cy = tx, ty
    else:
        cx, cy = (w // 2, h // 2)

    # Secondary intent: reduce chance of opponent taking close resource by pushing toward it if beneficial
    if resources:
        # Find opponent nearest; if they are closer to our target, shift toward next best resource
        opp_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = abs(rx - ox) + abs(ry - oy)
            if opp_best is None or d < opp_best[0] or (d == opp_best[0] and (rx, ry) < opp_best[1]):
                opp_best = (d, (rx, ry))
        if opp_best and opp_best[1] != (cx, cy):
            myd = abs(cx - sx) + abs(cy - sy)
            opd = opp_best[0]
            if opd < myd:
                # pick next best resource with tie-break away from opponent
                best2 = None
                for rx, ry in resources:
                    if (rx, ry) in obstacles:
                        continue
                    score = 2 * (abs(rx - sx) + abs(ry - sy)) - (abs(rx - ox) + abs(ry - oy))
                    key = (score, abs(rx - sx) + abs(ry - sy), (rx, ry))
                    if best2 is None or key < best2[0]:
                        best2 = (key, (rx, ry))
                cx, cy = best2[1]

    # Choose move: avoid obstacles/out of bounds; minimize distance to (cx, cy); tie-break also away from opponent
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to_target = abs(cx - nx) + abs(cy - ny)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        # Prefer moving toward resources/center; if tie, prefer being farther from opponent; then deterministic order
        key = (dist_to_target, -dist_to_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return [best_move[0], best_move[1]]