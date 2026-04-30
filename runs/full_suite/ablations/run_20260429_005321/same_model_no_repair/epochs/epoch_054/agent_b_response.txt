def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    blocked = set((x, y) for x, y in obstacles)

    def md(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # diagonal-allowed

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_t = None
    best_key = None
    for tx, ty in resources:
        if (tx, ty) in blocked:
            continue
        myd = md((sx, sy), (tx, ty))
        opd = md((ox, oy), (tx, ty))
        # If we can "contest" (we're no farther than opponent), strongly prefer that.
        contest = 1 if myd <= opd else 0
        key = (contest, (opd - myd), -myd)  # maximize
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    cur_d = md((sx, sy), (tx, ty))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_obstacle(x, y):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in blocked:
                    return 1
        return 0

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue
        d = md((nx, ny), (tx, ty))
        # Prefer decreasing distance to target; otherwise least worse.
        dist_improve = cur_d - d
        opp_d = md((nx, ny), (ox, oy))
        score = (dist_improve, -adj_obstacle(nx, ny), opp_d, -abs(nx - tx) - abs(ny - ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves invalid (shouldn't happen), stay put.
    return best_move