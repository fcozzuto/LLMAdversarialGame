def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, x, y):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy

    # Intercept/bypass: when resources are contested, bias toward cutting off opponent
    opp_near = 0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (dx or dy) and cheb(ox, oy, sx + dx, sy + dy) == 1:
                opp_near += 1
    opp_bias = 1.0 if opp_near >= 2 else 0.5

    # Precompute nearest resource distances from current positions for opponent-competition heuristic
    best_move = None
    best_val = -10**18
    best_d = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        # Evaluate all resources; prefer those where we gain relative proximity over opponent.
        val = -0.0
        min_my = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Main term: win the race for the resource; second: move toward it.
            rel = (oppd - myd)
            # Small tie-breakers to reduce dithering deterministically
            candidate = rel * 10.0 - myd * 0.25 + (oppd < myd) * (-3.0)
            if candidate > val:
                val = candidate
            if myd < min_my:
                min_my = myd
            if oppd < min_opp:
                min_opp = oppd

        if resources:
            # Strategic change: if opponent is nearer to most resources, move to a "cut" cell
            # near opponent to slow their ability to contest.
            if min_opp + 1 < min_my:
                # Move closer to opponent slightly but not at the cost of missing resources entirely.
                val -= opp_bias * cheb(nx, ny, ox, oy) * 2.2
            else:
                # Otherwise, keep pushing toward closest likely win.
                val += 0.1 * (min_opp - min_my)

        # Obstacle proximity penalty (avoid getting trapped)
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obs_set:
                    val -= 1.2

        # Deterministic tie-breaking
        my_to_opp = cheb(nx, ny, ox, oy)
        dscore = (my_to_opp, min_my if resources else 0, nx, ny)
        if (val > best_val) or (val == best_val and dscore < (best_d, best_d, best_move[0], best_move[1] if best_move else 0)):
            best_val = val
            best_move = (dx, dy)
            best_d = my_to_opp

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]