def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Choose resource: prefer ones we can reach sooner than opponent
    best_res = None
    best_val = -10**18
    for rx, ry in resources:
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        if (rx, ry) in obstacles:
            continue
        # value: advantage over opponent, slight tie-break to closer to us
        val = (od - sd) * 1000 - sd
        # penalize resources behind obstacles not considered; just keep deterministic
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res if best_res is not None else (sx, sy)

    # Evaluate candidate moves deterministically
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if best_res is None and (nx, ny) == (ox, oy):
            pass
        new_sd = dist2(nx, ny, tx, ty)
        new_od = dist2(nx, ny, ox, oy)
        # Prefer moving to resource; also prefer not clustering with opponent
        score = -new_sd * 10 + new_od
        # If staying on current cell (no resource), slightly deter unless forced
        if dx == 0 and dy == 0 and (sx, sy) not in resources:
            score -= 2
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If all candidate moves blocked, deterministically stay
    return [int(best_move[0]), int(best_move[1])]