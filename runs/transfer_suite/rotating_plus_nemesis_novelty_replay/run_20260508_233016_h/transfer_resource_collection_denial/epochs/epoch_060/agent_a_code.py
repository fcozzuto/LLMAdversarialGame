def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev for 8-direction step cost

    if not resources:
        return [0, 0]

    # Pick a target resource: prioritize one we can secure earliest; otherwise deny resources where opponent is closer.
    best = None
    tx = ty = None
    for rx, ry in resources:
        dm = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        secure = dm < do
        # Key: secure first, then earlier our arrival; else later our arrival relative to opponent (deny stronger).
        key = (0 if secure else 1, dm if secure else -(do - dm), do - dm, rx, ry)
        if best is None or key < best:
            best = key
            tx, ty = rx, ry

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_key = None

    # Evaluate local move: aim to reduce distance to target, but avoid giving opponent an earlier reach.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dm_next = dist(nx, ny, tx, ty)
        do_next = dist(ox, oy, tx, ty)
        secure_next = dm_next < do_next

        # Tie-break: prefer moves that increase our advantage; if still tied, prefer staying closer to opponent's side (deny pressure).
        adv = (do_next - dm_next)
        deny_pressure = dist(nx, ny, ox, oy)  # lower means more contest near opponent
        key = (
            0 if secure_next else 1,
            dm_next if secure_next else dm_next - adv,  # if not secure, still try not to fall too far behind
            -adv,
            deny_pressure,
            dx,
            dy,
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]