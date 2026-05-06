def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Row-sweep counter: avoid getting too close on the same row as opponent
        row_pen = 0
        if ny == oy and abs(nx - ox) <= 2:
            row_pen = 20 - 6 * abs(nx - ox)  # smaller penalty when farther

        # Choose a resource that favors us (small d_self) and deprioritizes opponent (large d_opp)
        best_obj = None
        for rx, ry in resources:
            d_self = abs(rx - nx) + abs(ry - ny)
            d_opp = abs(rx - ox) + abs(ry - oy)
            obj = d_self - 0.8 * d_opp  # prefer resources far from opponent, close to us
            if best_obj is None or obj < best_obj:
                best_obj = obj

        # Small tie-break: keep some distance from opponent to reduce immediate contest
        opp_sep = abs(nx - ox) + abs(ny - oy)
        val = best_obj + row_pen + 0.02 * (-opp_sep)  # prefer larger opp_sep => smaller -opp_sep

        if best is None or val < best or (val == best and (dx, dy) < best_move):
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]