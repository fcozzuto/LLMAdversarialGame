def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def min_obst_dist(x, y):
        best = 10**9
        for oxp, oyp in obstacles:
            d = cheb(x, y, oxp, oyp)
            if d < best:
                best = d
        return best if obstacles else 99

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if passable(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Pick a target resource that we can reach with relative advantage.
    if resources:
        best = None
        bestv = 10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; otherwise still allow if very close.
            v = ds - 0.9 * do
            # Small tie-break towards nearer absolute.
            v += 0.05 * ds
            if v < bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    # If opponent is already extremely close to the target, bias towards intercepting.
    opp_d_to_t = cheb(ox, oy, tx, ty)
    intercept = opp_d_to_t <= 2

    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        ds_next = cheb(nx, ny, tx, ty)
        ds_now = cheb(sx, sy, tx, ty)
        do_next = cheb(ox, oy, tx, ty)  # opponent position fixed this turn

        # Move score: reduce our distance; if intercepting, also try to not let opponent get further.
        score = 0
        score += (ds_now - ds_next) * 5.0
        score += (-ds_next) * (1.0 if not intercept else 2.0)

        # Keep some separation from opponent unless it helps to chase target.
        d_opp = cheb(nx, ny, ox, oy)
        if d_opp <= 1:
            score -= 8.0
        else:
            score += min(3.0, d_opp)  # slight preference for safer positions

        # Obstacle proximity penalty (discourage hugging tight areas).
        score += (min_obst_dist(nx, ny) - 1) * 0.2

        # Mild penalty for staying put.
        if dx == 0 and dy == 0:
            score -= 0.5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]