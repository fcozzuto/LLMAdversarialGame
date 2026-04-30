def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def near_obstacle(x, y):
        p = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (x+dx, y+dy) in occ:
                p += 1
        return p

    def toward_intercept(x, y, rx, ry):
        # Prefer moving along a shortest step toward a resource.
        dx = 0 if rx == x else (1 if rx > x else -1)
        dy = 0 if ry == y else (1 if ry > y else -1)
        return -(abs(rx - x - dx) + abs(ry - y - dy))

    # If resources exist, choose a move based on: reachable resource priority + opponent distance + obstacle avoidance.
    if not resources:
        # Fall back: keep distance from opponent and avoid obstacles
        best = (-10**18, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in occ:
                val = 2 * md(nx, ny, ox, oy) - 3 * near_obstacle(nx, ny)
                if val > best[0]:
                    best = (val, (dx, dy))
        return [best[1][0], best[1][1]]

    best_val = -10**18
    best_move = (0, 0)
    # Precompute resource info to bias against resources closer to opponent
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Base: stay away from opponent slightly, but don't ignore resources
        val = 0.8 * md(nx, ny, ox, oy) - 2.5 * near_obstacle(nx, ny)

        # Resource scoring: prefer resources where we are closer than opponent after the move.
        # Tie-break naturally by total value; deterministic by move iteration order.
        for rx, ry in resources:
            d_me = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            if d_me == 0:
                # Strongly commit to immediate collection
                val += 10**6
                continue

            # If opponent is closer, reduce attractiveness; if we can beat them, increase.
            beat = d_op - d_me
            # Encourage getting on track (shorter d_me) and beating opponent
            val += (3.0 * beat) - (1.4 * d_me)

            # Add a small nudge toward the direction of the target to break symmetry
            val += 0.05 * toward_intercept(nx, ny, rx, ry)

        # Extra: if near opponent, try to angle away from their direction
        # (prevents head-on races that often lose by blocking/shorter path)
        if md(nx, ny, ox, oy) <= 2:
            val -= 2.0 * md(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]