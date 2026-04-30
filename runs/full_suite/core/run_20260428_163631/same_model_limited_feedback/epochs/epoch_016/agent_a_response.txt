def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose target deterministically: best among resources by (prefer those we are closer to than opponent, else nearest)
    best = None
    best_key = None
    for rx, ry in resources:
        d1 = abs(rx - sx) + abs(ry - sy)
        d2 = abs(rx - ox) + abs(ry - oy)
        # Key: maximize advantage, then minimize our distance
        key = (-(d1 - d2), d1, (rx - ry))
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key
    if best is None:
        # No resources visible: move away from opponent if possible
        tx, ty = ox, oy
    else:
        tx, ty = best

    # Evaluate candidate moves
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Main objective: get closer to target
        dist_to_target = abs(tx - nx) + abs(ty - ny)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)

        # Secondary: if target exists, reduce chance opponent takes it by keeping between us and target
        # Simple proxy: if opponent is closer to our next position than to target, penalize
        if resources:
            # Estimate how close opponent could be to target from their current position
            opp_to_target = abs(tx - ox) + abs(ty - oy)
            # If opponent is already closer, we prioritize breaking that by increasing distance to opponent
            block_term = (opp_to_target - dist_to_opp)
        else:
            block_term = 0

        # Prefer moves that increase distance from opponent slightly and reduce staying still
        stay_pen = 0 if (dx == 0 and dy == 0) else -0.05
        val = (-dist_to_target) + 0.02 * dist_to_opp + 0.15 * block_term + stay_pen

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]