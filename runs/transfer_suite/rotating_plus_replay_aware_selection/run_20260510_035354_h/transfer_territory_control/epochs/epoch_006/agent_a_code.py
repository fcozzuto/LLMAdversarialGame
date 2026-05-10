def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    ax, ay = observation["self_position"]
    op = observation.get("opponent_position") or (ax, ay)
    ox, oy = op[0], op[1]

    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    targets = observation.get("unclaimed_cells") or []
    if not targets:
        targets = observation.get("resources") or []
    tg = [(p[0], p[1]) for p in targets]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    best = None
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        d_op = abs(nx - ox) + abs(ny - oy)
        # If adjacent to opponent, strongly prefer increasing distance
        threat = 0
        if d_op <= 1:
            threat = -1000

        # Prefer moving to the closest target (or center if none)
        if tg:
            d_t = min(abs(nx - tx) + abs(ny - ty) for tx, ty in tg)
            goal = -d_t
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            goal = -(abs(nx - cx) + abs(ny - cy))

        # Small deterministic tie-breaker favoring lexicographically earlier moves
        tie = -((dx + 1) * 10 + (dy + 1))

        sc = threat + goal + d_op + tie
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]