def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def clamp(x, y):
        return max(0, min(w - 1, x)), max(0, min(h - 1, y))
    def dist2(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        return dx * dx + dy * dy
    opp_range = max(1, (abs(sx - ox) + abs(sy - oy)) // 2 + 1)
    best = None; best_val = -10**18
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        # If moving onto a resource, strongly prioritize
        on_res = (nx, ny) in set((x, y) for x, y in resources)
        if resources:
            # Choose best target given this prospective move
            val = 0
            my_pos = (nx, ny)
            opp_pos = (ox, oy)
            for rx, ry in resources:
                r = (rx, ry)
                my_d = dist2(my_pos, r)
                op_d = dist2(opp_pos, r)
                # Prefer resources I'm closer to, but also avoid over-committing if opponent is too near.
                lead = op_d - my_d
                danger = 0
                if op_d <= opp_range * opp_range:
                    # If opponent is within a tactical radius, weight against targets they can snatch quickly
                    danger = 0.35 * (opp_range * opp_range - op_d)
                # Slight center bias to reduce corner traps
                center_bias = 0.02 * dist2(my_pos, (w / 2.0, h / 2.0))
                val += (lead - danger) - center_bias
                if on_res and r == (nx, ny):
                    val += 1e6
            # Normalize by number of resources to keep scale stable
            val /= max(1, len(resources))
        else:
            # No visible resources: drift toward center while keeping distance from opponent
            my_pos = (nx, ny)
            val = -0.05 * dist2(my_pos, (w / 2.0, h / 2.0)) + 0.2 * dist2(my_pos, (ox, oy))
        if val > best_val:
            best_val = val
            best = (dx, dy)
    if best is None:
        # Fallback: move away/toward based on opponent
        step = (-1 if ox > sx else (1 if ox < sx else 0), -1 if oy > sy else (1 if oy < sy else 0))
        dx, dy = step
        return [int(dx), int(dy)]
    return [int(best[0]), int(best[1])]