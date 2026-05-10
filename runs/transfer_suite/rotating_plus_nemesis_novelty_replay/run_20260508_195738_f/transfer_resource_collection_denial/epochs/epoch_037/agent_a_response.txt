def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target_score(px, py):
        if not resources:
            return None, -10**9
        best_res = None
        best_val = -10**9
        for rx, ry in resources:
            dS = manh(px, py, rx, ry)
            dO = manh(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; if tie, prefer smaller remaining distance; also bias toward fewer totals.
            val = 0
            if dS <= dO:
                val += 200 - 10 * dS
                val += 3 * (dO - dS)
            else:
                # Still move toward it if it is far ahead for us relative to opponent (soft)
                val += -20 - 3 * dS + 2 * (dO)
            # Small bias to avoid moving into "dead zones" (distance to nearest resource decreases)
            nearest = min(manh(px, py, ax, ay) for ax, ay in resources)
            val += -0.5 * nearest
            # Deterministic tie-breaker
            key = (val, -rx, -ry, -dS)
            if key > (best_val, 0, 0, 0):
                best_val = val
                best_res = (rx, ry)
        return best_res, best_val

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_eval = -10**18
    # If we are on a resource, stay (engine allows collect on that square if applicable), else steer.
    if (sx, sy) in set(resources):
        return [0, 0]

    res_set = set(resources)
    target, _ = best_target_score(sx, sy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate move by target score after move
        t, val = best_target_score(nx, ny)
        # Encourage progress to current best target to reduce oscillation
        if target is not None:
            val += 0.8 * (manh(sx, sy, target[0], target[1]) - manh(nx, ny, target[0], target[1]))
        # Penalize giving up position: prefer not to increase distance to opponent-too-close resources
        if resources:
            nearest_to_opp = min(manh(ox, oy, rx, ry) for rx, ry in resources)
            nearest_after = min(manh(nx, ny, rx, ry) for rx, ry in resources)
            val += 0.2 * (nearest_to_opp - nearest_after)
        # If move lands on a resource, make it dominant
        if (nx, ny) in res_set:
            val += 1000
        # Deterministic tie-breaker: prefer lower dx then dy
        eval_key = (val, -abs(dx), -abs(dy), -dx, -dy)
        if eval_key > (best_eval, 0, 0, 0, 0):
            best_eval = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]