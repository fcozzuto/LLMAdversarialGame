def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    valid_targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                valid_targets.append((x, y))
    if not valid_targets:
        return [0, 0]

    # Choose target: if opponent is closer, strongly prefer that resource (intercept).
    tx, ty = None, None
    best_t = None
    for x, y in valid_targets:
        self_d = man(sx, sy, x, y)
        opp_d = man(ox, oy, x, y)
        # smaller is better: intercept when opponent is closer
        # add tie-break to favor nearer overall.
        tscore = (0 if opp_d <= self_d else 1, abs(opp_d - self_d), self_d)
        if best_t is None or tscore < best_t:
            best_t = tscore
            tx, ty = x, y

    # Evaluate our next move: reduce distance to target while increasing opponent distance.
    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        self_to_t = man(nx, ny, tx, ty)
        opp_to_t = man(ox, oy, tx, ty)
        # also slightly avoid giving opponent immediate access by increasing their distance to the target after we move
        opp_future = man(ox, oy, tx, ty)
        # incorporate closeness to any remaining resource to keep progress if target unreachable
        alt = 10**9
        for x, y in valid_targets:
            d = man(nx, ny, x, y)
            if d < alt:
                alt = d
        # score tuple: minimize
        score = (
            self_to_t,
            opp_future,  # prefer states where target is not too close to opponent (since opp doesn't move)
            alt,
            man(nx, ny, sx, sy)  # prefer minimal deviation / stability
        )
        if best is None or score < best:
            best = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]