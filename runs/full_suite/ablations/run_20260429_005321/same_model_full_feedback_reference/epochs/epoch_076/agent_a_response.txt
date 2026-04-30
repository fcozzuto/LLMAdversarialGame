def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # If no visible resources, head toward the quadrant where resources typically are: opponent-opposite diagonal
    if not resources:
        tx = 1 if ox > sx else (-1 if ox < sx else 0)
        ty = 1 if oy > sy else (-1 if oy < sy else 0)
        for dx, dy in [(tx, ty), (tx, 0), (0, ty), (0, 0), (-tx, 0), (0, -ty)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose a target resource that we can reach sooner than the opponent; deterministically break ties by coord.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = d2(sx, sy, rx, ry)
        do = d2(ox, oy, rx, ry)
        # Prefer resources where we have a relative advantage; also slightly prefer closer absolute targets.
        key = (ds - 1.15 * do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # One-step lookahead: minimize distance to target while discouraging moves that let the opponent get closer
    # (relative advantage and local safety via obstacle checks).
    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = d2(nx, ny, rx, ry)

        # Opponent greedy-estimate: how close opponent is to the same resource after our move.
        # We don't know their move, so use current opponent distance to keep relative pressure.
        do2 = d2(ox, oy, rx, ry)

        # Local collision avoidance: prefer being farther from opponent.
        da2 = d2(nx, ny, ox, oy)

        score = (ds2 - 0.85 * do2, ds2, -da2, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]