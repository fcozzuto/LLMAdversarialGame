def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res_list = []
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Prefer resources we can reach no later than opponent; otherwise still prefer advantage.
        contest = 1 if myd <= opd else 0
        # Slightly penalize being closer to obstacles at target.
        adj = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (tx + dx, ty + dy) in obstacles:
                        adj += 1
        key = (contest, (opd - myd), -myd, -adj, tx, ty)
        res_list.append((key, (tx, ty)))
    if not res_list:
        return [0, 0]
    _, (tx, ty) = max(res_list, key=lambda z: z[0])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    cur_to_t = md(sx, sy, tx, ty)
    cur_to_o = md(sx, sy, ox, oy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = md(nx, ny, tx, ty)
        d_to_o = md(nx, ny, ox, oy)
        # If we can contest, keep tightening; else prioritize moving toward target but don't let opponent get safer.
        prog = cur_to_t - d_to_t
        # Safety: prefer fewer adjacent obstacles.
        adj = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx or ddy:
                    if (nx + ddx, ny + ddy) in obstacles:
                        adj += 1
        # Also lightly penalize moves that reduce our distance to opponent too much.
        key = (
            1 if md(nx, ny, tx, ty) <= md(ox, oy, tx, ty) else 0,
            prog,
            (d_to_o - cur_to_o),      # maximize increase from opponent
            -d_to_t,                 # closer to target
            -adj,
            dx, dy
        )
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]