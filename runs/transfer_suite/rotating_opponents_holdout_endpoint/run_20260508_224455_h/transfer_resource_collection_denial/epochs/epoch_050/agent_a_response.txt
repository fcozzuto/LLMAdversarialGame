def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((int(x), int(y)) for x, y in obs_list)

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def near_obs(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    return 1
        return 0

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_from(px, py):
        best = -10**9
        for rx, ry in resources:
            ds = md(px, py, rx, ry)
            do = md(ox, oy, rx, ry)
            adv = do - ds  # positive => we are closer
            trap = near_obs(rx, ry)
            # Prefer getting to a resource while also denying closer race to opponent.
            s = 3 * adv - ds - 2 * trap
            # Small tie-break toward higher "immediate closeness"
            if adv >= 0:
                s += 1
            if s > best:
                best = s
        return best

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # If we can reach a resource immediately, prioritize it strongly.
        immediate = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                immediate = 10**6
                break
        val = immediate + score_from(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]