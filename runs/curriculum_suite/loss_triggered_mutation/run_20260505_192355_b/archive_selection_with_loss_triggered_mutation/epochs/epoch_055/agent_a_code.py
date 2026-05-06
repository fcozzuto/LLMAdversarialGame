def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        # deterministic "escape": prefer move that increases distance from opponent
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            score = max(abs(nx - ox), abs(ny - oy))
            if score > best[1]:
                best = ([dx, dy], score)
        return best[0] if best[0] is not None else [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # obstacle proximity penalty (avoid getting stuck near walls)
    def near_obst(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obst:
                    pen += 1
        return pen

    # Interceptor-style: prioritize resources where we can arrive no later than opponent,
    # then minimize our arrival time; include local safety from obstacles.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        local_pen = 2 * near_obst(nx, ny)
        # Evaluate best resource target for this move
        move_val = -10**18
        for rx, ry in res:
            self_t = cheb((nx, ny), (rx, ry))
            opp_t = cheb((ox, oy), (rx, ry))
            # If we can beat opponent on arrival, prioritize strongly.
            # If not, deprioritize but still consider closer-than-opponent resources.
            advantage = opp_t - self_t
            # Add slight tie-breaker toward resources that are more central along approach.
            tie = -abs((rx - nx) - (ry - ny)) * 0.001
            val = (advantage * 1000) + (opp_t * 2) - (self_t * 3) + tie - local_pen
            if val > move_val:
                move_val = val
        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return best_move