def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # If we can capture a resource immediately, do it (deterministically: closest then lexicographic).
    immediate = [p for p in resources if p == (sx, sy)]
    if immediate:
        return [0, 0]
    best_imm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in resources:
            best_imm = (dx, dy)
            break
    if best_imm is not None:
        return [best_imm[0], best_imm[1]]

    # Otherwise: choose move that maximizes how many resources we can reach no later than the opponent,
    # then minimizes our distance to the best such resource, then blocks by maximizing distance advantage for worst case.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        beat = 0
        best_our = 10**9
        worst_gap = -10**9
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            if ds <= do:
                beat += 1
                if ds < best_our:
                    best_our = ds
            gap = do - ds  # positive => we are closer
            if gap > worst_gap:
                worst_gap = gap
        # key: more beat first, then smaller best_our, then larger worst_gap, then deterministic move order
        key = (-beat, best_our, -worst_gap, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]