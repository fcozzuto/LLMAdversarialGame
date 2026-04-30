def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Choose a single strategic target: maximize advantage against opponent.
    best_t = None
    best_k = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        k = (opd - myd, -myd, -rx * 8 - ry)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Predict opponent greedy step towards the target (deterministic tie-breaking).
    opd_now = cheb(ox, oy, tx, ty)
    best_opp = (ox, oy)
    best_opp_d = opd_now
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_opp_d or (d == best_opp_d and (dx, dy) < (best_opp[0] - ox, best_opp[1] - oy)):
            best_opp_d = d
            best_opp = (nx, ny)

    oxn, oyn = best_opp

    # Evaluate our candidate moves against the predicted opponent contest.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        if myd == 0:
            val = 10**9
        else:
            opd = cheb(oxn, oyn, tx, ty)
            # Prefer being closer than opponent after opponent's greedy move; then minimize our distance.
            val = (opd - myd) * 1000 - myd * 3
            # Slightly deter stepping into tight areas by favoring moves that keep distance from obstacles' corners.
            for ax, ay in obstacles:
                if ax == nx and ay == ny:
                    val -= 10**6
                else:
                    ad = cheb(nx, ny, ax, ay)
                    if ad <= 1:
                        val -= 5
        if best_val is None or val > best_val or (val == best_val and (dx