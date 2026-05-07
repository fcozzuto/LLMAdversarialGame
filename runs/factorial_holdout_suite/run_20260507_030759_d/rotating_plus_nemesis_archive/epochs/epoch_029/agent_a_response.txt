def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # Default: drift toward closer side of board away from opponent a bit
        dx = 0
        if sx < w - 1 and sx >= ox:
            dx = 1
        elif sx > 0 and sx <= ox:
            dx = -1
        dy = 0
        if sy < h - 1:
            dy = 1
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst:
            return [dx, dy]
        return [0, 0]

    res = []
    for r in resources:
        try:
            res.append((int(r[0]), int(r[1])))
        except Exception:
            pass
    res.sort()

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        my_pos = (nx, ny)

        # Evaluate best resource after this move (maximize "arrive first" advantage).
        my_best = -10**18
        for r in res:
            my_d = md(my_pos, r)
            op_d = md((ox, oy), r)
            # Primary: we want op_d - my_d large (we reach earlier).
            # Secondary: smaller my_d.
            # Tertiary: deterministic preference by resource order.
            val = (op_d - my_d) * 1000 - my_d * 3
            if op_d == my_d:
                val += 5  # slight bias to tie (our move might matter)
            my_best = max(my_best, val)

        # Small repulsion from opponent to reduce chance of being out-raced near them.
        rep = -md(my_pos, (ox, oy)) * 0.1
        # Mild preference for moving (avoid getting stuck) unless it harms.
        step_bias = 0 if (dx == 0 and dy == 0) else 1
        val = my_best + rep + step_bias

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]