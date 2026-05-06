def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    if not resources:
        # Fallback: drift toward center unless blocked
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_key = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny):
                    continue
                key = (abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy), dx, dy)
                if best_key is None or key < best_key:
                    best_key = key
                    best = [dx, dy]
        return best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        # Chebyshev fits diagonal movement well
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Precompute opponent-to-resource distances
    oppd = {(rx, ry): dist((ox, oy), (rx, ry)) for (rx, ry) in resources}

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd_min = None
        adv_sum = 0.0
        for (rx, ry) in resources:
            sd = dist((nx, ny), (rx, ry))
            if sd_min is None or sd < sd_min:
                sd_min = sd
            od = oppd[(rx, ry)]
            # Prefer resources we can reach sooner; discourage ones opponent is already closer to
            # Slightly reward getting within immediate pickup range.
            if sd <= od:
                adv_sum += (od - sd + (1 if sd == 0 else 0))
            else:
                adv_sum -= (sd - od) * 0.75
        # Tie-break: maximize advantage, then closest-to-some-resource, then keep moving away from being "cornered"
        key = (-adv_sum, sd_min if sd_min is not None else 999, (abs(nx - (w - 1)) + abs(ny - (h - 1))), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]