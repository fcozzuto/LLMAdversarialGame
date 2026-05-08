def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        return default

    sx, sy = pos(observation.get("self_position", None), (0, 0))
    ox, oy = pos(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if is_free(x, y):
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue

        # Evaluate the best contested resource after this step.
        local_best = -10**18
        local_best_dist = 10**9
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # Positive favors taking a resource before opponent; tie-break favors shorter self distance.
            sc = (od - sd) * 100 - sd
            if sc > local_best or (sc == local_best and sd < local_best_dist):
                local_best = sc
                local_best_dist = sd

        # Small preference to stay closer to any resource cluster (avoids dead-ends near one resource).
        min_self_to_any = min(man(nx, ny, tx, ty) for tx, ty in resources)
        score_move = local_best - 0.1 * min_self_to_any
        if score_move > best_score:
            best_score = score_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]