def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources_raw = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    resources = []
    for p in resources_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da + db

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves.sort(key=lambda d: (d[0], d[1]))

    def best_from(px, py):
        best = None
        for tx, ty in resources:
            sd = man(px, py, tx, ty)
            od = man(ox, oy, tx, ty)
            adv = od - sd
            key = (adv, -sd, tx, ty)
            if best is None or key > best[0]:
                best = (key, sd, adv, (tx, ty))
        return best[1], best[2], best[3]

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd, adv, (tx, ty) = best_from(nx, ny)

        # Prefer moves that increase advantage; then reduce self distance; then head toward a deterministic target.
        # Also lightly avoid moving closer to opponent's nearest point by using current adv computation.
        key = (adv, -sd, -man(nx, ny, ox, oy), tx, ty, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]