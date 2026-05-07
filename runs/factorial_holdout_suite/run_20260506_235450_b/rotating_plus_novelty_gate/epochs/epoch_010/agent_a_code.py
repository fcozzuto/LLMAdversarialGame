def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick next position that maximizes "take-the-resource first" advantage.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # If we can capture immediately, prioritize.
        immediate = (nx, ny) in set((r[0], r[1]) for r in resources)
        if immediate:
            val = 10**9
        else:
            # Evaluate best resource we can realistically race for from next state.
            val = -10**12
            for rx, ry in resources:
                my_d = man(nx, ny, rx, ry)
                op_d = man(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent; slightly prefer closer targets.
                k = (op_d - my_d) * 100 - my_d
                if k > val:
                    val = k

            # Nudge to avoid moving away from all resources when ties happen.
            # (Compute min distance-to-any-resource from next.)
            min_d = None
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if min_d is None or d < min_d:
                    min_d = d
            val -= (min_d if min_d is not None else 0)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]