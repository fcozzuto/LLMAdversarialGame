def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b):
        return max(abs(b[0] - a[0]), abs(b[1] - a[1]))

    if not resources:
        return [0, 0]

    best = None
    best_move = (0, 0)

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        move_best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = dist((nsx, nsy), (rx, ry))
            od = dist((ox, oy), (rx, ry))

            # Prefer resources we beat opponent on; tie-break by shorter self distance.
            diff = od - sd
            if diff > 0:
                # Large positive for beating opponent; slightly prefer nearer resource.
                key = (1, diff, -sd, rx, ry)
            elif diff == 0:
                # Likely contested: still prefer shorter self distance, then deterministic.
                key = (0, 0, -sd, rx, ry)
            else:
                # Behind: discourage strongly, but keep as fallback.
                key = (-1, diff, -sd, rx, ry)

            if move_best_key is None or key > move_best_key:
                move_best_key = key

        if move_best_key is None:
            continue

        if best is None or move_best_key > best:
            best = move_best_key
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]