def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    if not resources:
        return [0, 0]

    best_t = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        d_us = abs(rx - sx) + abs(ry - sy)
        d_op = abs(rx - ox) + abs(ry - oy)
        val = d_us - 0.6 * d_op  # prefer resources we are closer to than opponent
        if best_val is None or val < best_val:
            best_val = val
            best_t = (rx, ry)
    if best_t is None:
        best_t = resources[0]
    tx, ty = best_t

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= observation["grid_width"] or ny >= observation["grid_height"]:
            continue
        hit_obstacle = (nx, ny) in obs_set
        # If engine would keep us in place due to invalid move, simulate by staying.
        # But we can mainly avoid obstacle tiles deterministically.
        if hit_obstacle:
            continue
        d1 = abs(tx - nx) + abs(ty - ny)
        d_op = abs(tx - ox) + abs(ty - oy)
        # Small tie-breaker: move that also reduces opponent distance to the target less is preferred
        score = d1 - 0.15 * d_op + 0.01 * (dx == 0 and dy == 0)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    # If all moves are blocked by obstacles, pick a deterministic non-out-of-bounds move (may hit obstacle; engine will keep position)
    if best_score is None:
        for dx, dy in [(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"]:
                return [dx, dy]
        return [0, 0]

    return best_move