def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    px, py = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    # Pick a target: nearest unclaimed; if none, nearest opponent territory to flip.
    best_target = None
    best_d = 10**9
    if unclaimed:
        for tx, ty in unclaimed:
            d = abs(tx - sx) + abs(ty - sy)
            if d < best_d:
                best_d = d
                best_target = (tx, ty)
    else:
        for tx, ty in opp_t:
            d = abs(tx - sx) + abs(ty - sy)
            if d < best_d:
                best_d = d
                best_target = (tx, ty)
    if best_target is None:
        target = (px, py)
    else:
        target = best_target
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: order as listed.
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        gain = 0
        if cell in unclaimed:
            gain += 3
        elif cell in opp_t:
            gain += 5  # flipping on entry
        elif cell in self_t:
            gain += 0
        # Distance shaping toward target; slight preference to reduce distance to opponent when tied.
        dist_t = abs(nx - tx) + abs(ny - ty)
        dist_p = abs(nx - px) + abs(ny - py)
        score = gain * 100 - dist_t * 2 - dist_p * 0.2
        # Encourage staying mobile: avoid local dead-ends by preferring non-stationary when scores equal.
        if dx == 0 and dy == 0:
            score -= 0.1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]