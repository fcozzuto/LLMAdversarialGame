def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_penalty(x, y):
        if not inb(x, y): 
            return 10**9
        if (x, y) in obstacles:
            return 10**8
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 3
        return p

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            p = obstacle_penalty(nx, ny)
            if p >= 10**8:
                continue
            val = -p - 0.01*(abs(nx - cx) + abs(ny - cy))
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)
        return [best_move[0], best_move[1]]

    # Deterministic two-agent contest heuristic: maximize (opponent_farther - us_closer),
    # with a small bias toward centralizing while avoiding obstacles.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        p = obstacle_penalty(nx, ny)
        if p >= 10**8:
            continue

        center_bias = -0.02 * (abs(nx - cx) + abs(ny - cy))
        # Target selection: evaluate all resources, but prefer the single best contest target.
        best_target = -10**18
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Primary: contest advantage (positive if we end up closer than opponent).
            adv = (opd - myd)
            # Secondary: prefer closer resources overall, but only when contest is competitive.
            closeness = -0.15 * myd
            # Slight preference for resources toward our side of the map (reduce path crossing).
            side = 0.0
            if sx <= (w - 1) / 2.0:
                side = -0.01 * ty
            else:
                side = -0.01 * (h - 1 - ty)
            val = adv + closeness + side
            if val > best_target:
                best_target = val

        # Reduce value if move goes near obstacles; also reward staying put if already best.
        val = best_target + center_bias - 0.35 * p
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]