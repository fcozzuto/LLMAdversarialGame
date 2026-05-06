def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def cell_block(cell):
        # Prefer moves that increase my chance to beat opponent to some nearby resource.
        x, y = cell
        my = man(sx, sy, x, y)
        opp = man(ox, oy, x, y)
        return (opp - my, -my)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    parity = int(observation.get("turn_index", 0)) & 1

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Evaluate by the best target I can reach that the opponent can plausibly contest.
        local_best = -10**18
        for i, (rx, ry) in enumerate(res):
            t_my = man(nx, ny, rx, ry)
            t_op = man(ox, oy, rx, ry)

            # Deterministic target diversification: alternate which indices to emphasize.
            # (acts like a stable "strategy mode" rather than randomness)
            mode_boost = 4 if ((i + parity) % 2 == 0) else 0

            # Core objective: maximize advantage in arrival time; slight preference to closer resources.
            advantage = (t_op - t_my) * 10 + mode_boost
            closeness = -t_my
            block_pressure = -abs((nx - rx) + (ny - ry))  # small tie-breaker for directionality
            val = advantage * 100 + closeness * 2 + block_pressure
            if val > local_best:
                local_best = val

        # Secondary objective: avoid moving toward positions that worsen overall contesting posture.
        # Compare my distance-to-resources vs opponent's from the candidate.
        posture = -min(manhattan for manhattan in [min(man(nx, ny, r[0], r[1]) for r in res)])
        opp_posture = min(man(ox, oy, r[0], r[1]) for r in res)
        total = local_best + (posture - opp_posture) * 2

        if total > best_score:
            best_score = total
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]