def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_cells = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_cells.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))
    if not unclaimed:
        return [0, 0]

    # Manhattan distance (territory flip on entry doesn't require exact pathing; movement is greedy).
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer cells where we are closer than opponent, and that are nearer overall.
    best = None
    best_key = None
    for cx, cy in unclaimed:
        if (cx, cy) in obs_cells:
            continue
        ds = man((sx, sy), (cx, cy))
        do = man((ox, oy), (cx, cy))
        # edge emphasis to contest the archetype, and slight preference for inner expansion
        edge = (cx == 0 or cy == 0 or cx == w - 1 or cy == h - 1)
        score = (do - ds) + (0.35 if edge else 0.0) - 0.02 * ds
        # deterministic tie-break by coordinates
        key = (-score, cx, cy)
        if best_key is None or key < best_key:
            best_key = key
            best = (cx, cy)

    if best is None:
        return [0, 0]

    tx, ty = best
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    candidates = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs_cells:
                continue
            # Prefer moves that reduce distance to target; break ties toward the move that advances both axes.
            dist = man((nx, ny), (tx, ty))
            axis_adv = (1 if dx != 0 else 0) + (1 if dy != 0 else 0)
            candidates.append((dist, -axis_adv, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]