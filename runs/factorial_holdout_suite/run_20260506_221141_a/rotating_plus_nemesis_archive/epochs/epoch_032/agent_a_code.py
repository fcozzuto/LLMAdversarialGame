def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources_raw = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    if not (isinstance(sx, int) and isinstance(sy, int) and 0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score_from(px, py):
        # Higher score is better: prefer resources where we are faster, then faster absolute, then safer (not too close to opponent).
        best = -10**9
        for tx, ty in resources:
            my_d = man(px, py, tx, ty)
            op_d = man(ox, oy, tx, ty)
            # margin > 0 means we can reach first under equal movement assumptions
            margin = op_d - my_d
            # Tie-break: if margins equal, choose smaller my_d; also mildly penalize being closer than opponent to avoid stepping into races we can't win.
            val = margin * 100 - my_d
            if my_d == op_d:
                val -= (man(tx, ty, sx, sy) - man(tx, ty, ox, oy)) * 2
            # Favor picking resources that are not immediately behind obstacles distance-wise (local proxy: keep a bit farther from opponent)
            val -= (man(px, py, ox, oy) == 0) * 50
            if val > best:
                best = val
        return best

    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = score_from(nx, ny)
        # Deterministic tie-break: prefer moves that reduce our distance to the best target more.
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
        elif v == best_val:
            if man(nx, ny, ox, oy) < man(sx, sy, ox, oy):
                best_move = [dx, dy]

    # If all moves blocked (shouldn't happen), stay still.
    return [int(best_move[0]), int(best_move[1])]