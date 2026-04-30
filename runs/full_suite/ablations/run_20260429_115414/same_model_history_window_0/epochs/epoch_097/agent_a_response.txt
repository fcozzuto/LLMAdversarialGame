def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        dx = 0
        dy = 0
        candidates = [(dx, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for c in sorted(candidates):
            nx, ny = sx + c[0], sy + c[1]
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [c[0], c[1]]
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best = None
    for r in resources:
        tx, ty = r
        if (tx, ty) in obstacles:
            continue
        ds = dist((sx, sy), (tx, ty))
        do = dist((ox, oy), (tx, ty))
        # Prefer resources we are closer to; tie-break deterministically by distance and coordinates
        key = (-(do - ds), ds, tx, ty)
        if best is None or key < best[0]:
            best = (key, tx, ty)
    _, tx, ty = best

    # Choose move that reduces distance to target while not stepping into obstacles
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), (tx, ty))
        # Mildly avoid moving onto opponent
        collide_penalty = 1 if (nx, ny) == (ox, oy) else 0
        key = (d, collide_penalty, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]