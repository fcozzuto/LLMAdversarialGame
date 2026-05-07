def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set(map(tuple, obstacles)) if obstacles else set()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose target that opponent is most threatening to collect next; race/deny it.
    best_t_opp = None
    best_d_opp = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if best_d_opp is None or d < best_d_opp:
            best_d_opp = d
            best_t_opp = (rx, ry)

    # Also consider our nearest, but with smaller weight to stay denial-focused.
    best_t_self = None
    best_d_self = None
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if best_d_self is None or d < best_d_self:
            best_d_self = d
            best_t_self = (rx, ry)

    def density(x, y):
        # small neighborhood resource clustering
        r = 2
        cnt = 0
        for rx, ry in resources:
            if cheb(x, y, rx, ry) <= r:
                cnt += 1
        return cnt

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        penalty = 50 if (nx, ny) in obs_set else 0

        rx1, ry1 = best_t_opp
        our_d1 = cheb(nx, ny, rx1, ry1)
        opp_d1 = cheb(ox, oy, rx1, ry1)

        rx2, ry2 = best_t_self
        our_d2 = cheb(nx, ny, rx2, ry2)

        # Denial objective: minimize our distance while also reducing lead gap.
        score = (our_d1 - 0.9 * opp_d1) + 0.15 * our_d2 - 0.35 * density(nx, ny) + penalty

        # Small deterministic tie-break favoring progress toward target.
        if best_score is None or score < best_score or (score == best_score and (abs(nx - rx1) + abs(ny - ry1)) < (abs(sx - rx1) + abs(sy - ry1))):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]