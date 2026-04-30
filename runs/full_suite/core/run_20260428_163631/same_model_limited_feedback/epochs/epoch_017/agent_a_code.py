def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    opp_d = {}

    for rx, ry in resources:
        opp_d[(rx, ry)] = dist(ox, oy, rx, ry)

    def move_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if not inside(nx, ny):
            return -10**9
        best = -10**9
        for rx, ry in resources:
            d_self = dist(nx, ny, rx, ry)
            d_opp = opp_d[(rx, ry)]
            if d_self <= d_opp:
                # Prefer resources we can plausibly claim, and also prefer denying them (larger gap).
                s = (d_opp - d_self) * 1000 - d_self
            else:
                # Still consider reachable resources, but strongly prefer ones we aren't losing.
                s = -d_self - (d_self - d_opp) * 50
            if s > best:
                best = s
        # If no resources exist, simply move away from opponent to reduce contention.
        if not resources:
            best = -dist(nx, ny, ox, oy)
        # Small tie-break: avoid getting too close to obstacles by penalizing proximity.
        if obstacles:
            min_ob = min((nx - ax) * (nx - ax) + (ny - ay) * (ny - ay) for ax, ay in obstacles)
            best -= min_ob * 0.01
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = move_score(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]