def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        # Immediate value if stepping onto a resource
        on_res = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0

        # We choose the resource that gives best "contest edge":
        # advantage = (opp_d - self_d). Positive means we get there sooner.
        # If no positive advantage exists, pick the move that minimizes opponent pressure.
        chosen = None
        chosen_key = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            # Prefer: immediate pickup, then higher adv, then lower own distance, then lower opponent distance
            key = (adv, -sd, -od)
            if chosen_key is None or key > chosen_key:
                chosen_key = key
                chosen = (adv, sd, od)

        adv, sd, od = chosen
        # Additional anti-denial: slightly prefer being closer to "most contested" resource when we're behind.
        if adv <= 0:
            # compute minimal opponent distance over resources
            opp_pressure = min(man(ox, oy, rx, ry) for rx, ry in resources)
            key = (on_res, -adv, sd, -od, opp_pressure)
        else:
            key = (on_res, -adv, sd, -od, 0)

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]