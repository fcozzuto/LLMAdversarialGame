def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0), (1, 0),
             (-1, 1),  (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # hold position if nothing to do
        for dx, dy in moves:
            if dx == 0 and dy == 0 and valid(sx, sy):
                return [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def md(a, b, c, d):
        v = a - c
        if v < 0: v = -v
        u = b - d
        if u < 0: u = -u
        return v + u

    # pick target resource deterministically: minimize our distance; break ties by position
    best_r = None
    best_d = None
    for rx, ry in resources:
        d = md(sx, sy, rx, ry)
        if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_r):
            best_d = d
            best_r = (rx, ry)
    rx, ry = best_r

    # score each immediate move: prefer progress to target, and prevent opponent from being much closer
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my = md(nx, ny, rx, ry)
        op = md(ox, oy, rx, ry)
        # higher is better
        score = -my
        # if opponent is closer than us, slightly penalize
        if op < my:
            score -= 5
        # avoid moves that wander away from both
        score += 0 if md(nx, ny, ox, oy) == 0 else 0
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: smaller (dx,dy) lexicographically
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]