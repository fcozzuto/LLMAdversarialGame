def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) + abs(dy)

    # Pick target resource: prefer ones we are closer to than opponent (or significantly ahead).
    best_res = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds - int(do * 0.95), ds, do, rx, ry)  # deterministic
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    # If no viable resources, move toward center while keeping away from opponent.
    if best_res is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best_move = (0, 0)
        best_score = None
        for dx, dy in deltas:
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            sdist = abs(nx - tx) + abs(ny - ty)
            odist = dist((nx, ny), (ox, oy))
            score = (sdist, -odist, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best_res
    # Choose move that minimizes distance to target; add small bias to avoid squares near opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        # If we can reach target this turn, prioritize strongly.
        if (nx, ny) == (tx, ty):
            score = (-10**6, 0, dx, dy)
        else:
            od = dist((nx, ny), (ox, oy))
            # Encourage being farther from opponent while still progressing.
            score = (nd, -od // 2, abs(dx) + abs(dy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]