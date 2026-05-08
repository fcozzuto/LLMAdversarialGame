def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    self_cells = observation.get("self_territory", [])
    opp_cells = observation.get("opponent_territory", [])
    unclaimed = observation.get("unclaimed_cells", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sx, sy = self_pos
    ox, oy = opp_pos
    self_set = set((x, y) for x, y in self_cells)
    opp_set = set((x, y) for x, y in opp_cells)
    behind = observation.get("self_territory_count", 0) < observation.get("opponent_territory_count", 0)
    # target selection
    tx, ty = ox, oy
    bestd = 10**9
    if behind:
        # attack: nearest opponent territory cell
        for x, y in opp_set:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
                tx, ty = x, y
    else:
        # expand: nearest unclaimed cell
        if unclaimed:
            for x, y in unclaimed:
                d = abs(x - sx) + abs(y - sy)
                if d < bestd:
                    bestd = d
                    tx, ty = x, y
        else:
            # no unclaimed: head to nearest opponent cell
            for x, y in opp_set:
                d = abs(x - sx) + abs(y - sy)
                if d < bestd:
                    bestd = d
                    tx, ty = x, y
    # evaluate moves
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        gain = 0
        if (nx, ny) in opp_set:
            gain = 1
        elif (nx, ny) not in self_set:
            gain = 1  # unclaimed or effectively free
        # prefer getting closer to target, but if attacking, also prioritize breaking contact
        dist = abs(tx - nx) + abs(ty - ny)
        contact = abs(nx - ox) + abs(ny - oy)
        score = gain * (200 if behind else 140) - dist
        if behind:
            score += -contact * 0.5
        else:
            # avoid wandering into opponent territory too early if ahead
            score += (0.1 if (nx, ny) in opp_set else 0.0)
        # deterministic tie-breaker: fixed order already, but add small stable preference
        score += -0.01 * (abs(dx) + abs(dy))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move