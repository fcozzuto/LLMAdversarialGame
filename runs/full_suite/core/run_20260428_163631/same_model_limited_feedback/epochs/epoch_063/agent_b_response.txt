def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        dx = 0
        dy = 0
        # drift toward opponent to deny
        if ox > sx:
            dx = 1
        elif ox < sx:
            dx = -1
        if oy > sy:
            dy = 1
        elif oy < sy:
            dy = -1
        return [dx, dy]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer resources closer than opponent; otherwise prefer those where we're not far behind.
        # Tie-break deterministically by coordinates.
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Score by resulting distance to target, with slight penalty if stepping near opponent.
        d_to = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # Also avoid giving opponent immediate reach if possible.
        candidates.append((d_to, -d_opp, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Choose smallest distance to target; tie-break by maximizing opponent distance, then deterministic dx,dy.
    candidates.sort(key=lambda t: (t[0], -t[1], t[2], t[3]))
    _, _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]