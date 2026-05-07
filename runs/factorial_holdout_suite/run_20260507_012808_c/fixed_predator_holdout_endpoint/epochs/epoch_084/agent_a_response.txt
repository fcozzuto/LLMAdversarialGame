def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    best = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate this move by targeting the most "winnable" nearby resource.
        local_best = None
        for tx, ty in resources:
            sd = manh(nx, ny, tx, ty)
            od = manh(ox, oy, tx, ty)
            advantage = od - sd  # positive means we are closer
            # Tie-break: prefer collecting sooner; prefer big advantage; discourage moving far.
            val = (advantage, -sd, -abs(ox - tx) - abs(oy - ty))
            if local_best is None or val > local_best[0]:
                local_best = (val, tx, ty)

        if local_best is None:
            continue
        val = local_best[0]

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]