def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role)
    if not (is_evader or is_pursuer):
        is_evader = False
        is_pursuer = True

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def cheb(x, y):
        dx = x - ox
        if dx < 0: dx = -dx
        dy = y - oy
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obs(x, y):
        c = 0
        for nx in (x - 1, x, x + 1):
            if nx < 0 or nx >= w:
                continue
            for ny in (y - 1, y, y + 1):
                if ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obs:
                    c += 1
        return c

    def move_blocked_tendency(x, y):
        if (x, y) in obs:
            return 1000
        c = adj_obs(x, y)
        return c

    best_move = [0, 0]
    best_val = None

    # Deterministic tie-breaker order: fixed moves list
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        d = cheb(nx, ny)
        o = move_blocked_tendency(nx, ny)

        if is_pursuer:
            val = -d * 10 - o * 2
        else:
            # evader: maximize distance, also prefer fewer adjacent obstacles
            val = d * 10 - o * 2

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move