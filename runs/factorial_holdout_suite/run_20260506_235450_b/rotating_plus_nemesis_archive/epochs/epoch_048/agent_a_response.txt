def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = (10**9, 10**9, 10**9, 0, 0)  # (key1, key2, key3, rx, ry)
    best_res = None

    # Choose target resource: we want smallest (our_dist - opp_dist), then smallest our_dist.
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key1 = sd - od
        key2 = sd
        key3 = (rx * 31 + ry)  # deterministic tie-break
        if (key1, key2, key3) < (best[0], best[1], best[2]):
            best = (key1, key2, key3, rx, ry)
            best_res = (rx, ry)

    tx, ty = best_res
    # If target is blocked (shouldn't happen), fall back to any resource.
    if (tx, ty) in obs and resources:
        tx, ty = min(resources, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))

    # Evaluate each move by resulting position.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Greedy: choose move that improves capture likelihood to the best (for current position) resource.
        # Denier opponent: also account for opponent's relative distance to that same resource.
        move_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            key = (sd - od, sd, rx * 31 + ry)
            if move_best is None or key < move_best[0]:
                move_best = (key, rx, ry)
        key = move_best[0]

        # Extra tie-break: prefer progress toward our chosen target.
        tgt_prog = man(nx, ny, tx, ty)
        full_key = (key[0], key[1], tgt_prog, abs(dx) + abs(dy), (nx * 17 + ny))
        if best_move_key is None or full_key < best_move_key:
            best_move_key = full_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]