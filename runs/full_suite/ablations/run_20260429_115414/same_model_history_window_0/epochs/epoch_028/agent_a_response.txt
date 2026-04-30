def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # If no resources, drift toward center and away from opponent
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                    continue
                d = abs(nx - tx) + abs(ny - ty)
                # mild repulsion from opponent
                rep = -0.1 * (abs(nx - ox) + abs(ny - oy))
                val = d + rep
                if val < best[0]:
                    best = (val, dx, dy)
        return [best[1], best[2]]
    # Choose resource to compete for: minimize (self_dist - opponent_dist), tie-break by self_dist
    best_r = None
    best_key = (10**9, 10**9)
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (sd - od, sd)
        if key < best_key:
            best_key = key
            best_r = (rx, ry)
    rx, ry = best_r
    # Move one step toward target with obstacle avoidance; deterministically try best among legal moves
    target_dx = 0 if rx == sx else (1 if rx > sx else -1)
    target_dy = 0 if ry == sy else (1 if ry > sy else -1)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            # Primary: reduce distance to target
            d1 = abs(rx - nx) + abs(ry - ny)
            # Secondary: prefer step alignment with target direction
            align = - (dx - target_dx) * (dx - target_dx) - (dy - target_dy) * (dy - target_dy)
            # Tertiary: avoid getting too close to opponent (slight)
            opp = abs(nx - ox) + abs(ny - oy)
            # Composite: smaller is better; opp is used as bonus via negative weight
            val = d1 + 0.05 * (4 - opp)  # discourages being near opponent
            moves.append((val, -align, abs(dx), abs(dy), dx, dy))
    moves.sort()
    if moves:
        return [moves[0][4], moves[0][5]]
    return [0, 0]