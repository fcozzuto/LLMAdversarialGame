def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target resource: prefer ones we are closer to than opponent.
    best = None
    best_score = None
    for r in resources:
        rx, ry = r
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = (ds - do, ds, rx, ry)  # lexicographic tie-break
        if best_score is None or score < best_score:
            best_score = score
            best = (rx, ry)
    if best is None:
        return [0, 0]

    tx, ty = best

    # Deterministic move: among legal neighbors (including stay), minimize distance to target.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = None
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        v = dist((nx, ny), (tx, ty))
        # Secondary: keep pressure by also considering opponent distance to target (prefer moves that increase their disadvantage)
        opp_adv = dist((ox, oy), (tx, ty)) - dist((nx, ny), (tx, ty))
        cand = (v, -opp_adv, dx, dy)
        if best_v is None or cand < best_v:
            best_v = cand
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]