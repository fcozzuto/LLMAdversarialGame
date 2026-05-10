def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    best_score = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Evaluate by choosing the resource that maximizes our "win" margin
        # margin = (opp_dist - self_dist), prefer earlier/lower distance too.
        # If we can't beat opponent on any resource this turn, pick the move that
        # minimizes (self_dist - opp_dist) and also reduces our distance.
        local_best = None
        local_tie = None
        feasible = False

        for rx, ry in resources:
            if not ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # win_margin positive means we arrive sooner
            margin = od - sd

            # Strongly prefer positive margins; then prefer larger margin; then smaller sd.
            # Deterministic tie-break: fixed ordering by (rx,ry).
            if margin > 0:
                feasible = True
                key = (1, margin, -sd, -rx, -ry)
            else:
                key = (0, margin, -sd, -rx, -ry)

            if local_best is None or key > local_best:
                local_best = key
                local_tie = (rx, ry)

        # Convert local_best into a global score
        if feasible:
            # Prefer moves that yield any positive win margin, and among those, maximize key.
            score = local_best
        else:
            # No guaranteed win: minimize our relative disadvantage by maximizing margin (<=0), then sd.
            # local_best already uses (0, margin, -sd, ...)
            score = local_best

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]