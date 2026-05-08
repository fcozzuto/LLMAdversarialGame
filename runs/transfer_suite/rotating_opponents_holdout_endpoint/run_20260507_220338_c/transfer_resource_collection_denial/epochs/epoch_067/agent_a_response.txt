def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resset.add((p[0], p[1]))

    if (sx, sy) in resset:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick best target resource for us: maximize (opponent distance - self distance),
    # with a time pressure to commit toward closer targets as time runs out.
    best_target = None
    best_key = None
    t = turns_remaining if turns_remaining is not None else 0
    for rx, ry in resset:
        if (rx, ry) in obst:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        time_commit = (sd + 1) + max(0, (t - 8)) * 0.02  # prefers shorter sd later
        key = (adv, -time_commit, -sd, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Choose move that maximizes our advantage after the move; prefer staying in bounds.
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        adv_after = d_opp - d_self
        # Slightly prefer reducing our distance even when tied.
        key = (adv_after, -d_self, -(abs(ox - nx) + abs(oy - ny)))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move