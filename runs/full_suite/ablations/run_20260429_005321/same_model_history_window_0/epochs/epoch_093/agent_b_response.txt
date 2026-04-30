def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    oxp, oyp = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])
    dx_dy = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose target: nearest resource by Chebyshev distance; tie-break by coordinates.
    if resources:
        best_t = None
        best_d = None
        for rx, ry in resources:
            d = max(abs(rx - sx), abs(ry - sy))
            if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_t):
                best_d = d
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No resources: move to center-ish deterministically.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in dx_dy:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        # Prefer moves that reduce distance to target.
        dist_t = max(abs(tx - nx), abs(ty - ny))
        dist_o = max(abs(oxp - nx), abs(oyp - ny))
        on_resource = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0

        # Score: prioritize grabbing resources, then getting closer to target.
        score = (on_resource, -dist_t, dist_o)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]