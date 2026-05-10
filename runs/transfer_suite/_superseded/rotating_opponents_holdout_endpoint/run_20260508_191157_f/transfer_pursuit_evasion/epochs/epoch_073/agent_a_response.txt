def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = observation.get("self_role", "pursuer")
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
    deltas = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        if role == "pursuer":
            corner_bias = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            # Strongly minimize distance; tie-break toward corners.
            score = dist * 1000 + corner_bias
            better = (best_score is None) or (score < best_score)
        else:
            far_corner = max(abs(cx - ox) + abs(cy - oy) for cx, cy in corners)
            # Strongly maximize distance; tie-break toward being in the farthest corner.
            score = -dist * 1000 - far_corner
            better = (best_score is None) or (score < best_score)

        if better:
            best_score = score
            best_move = [dx, dy]

    return best_move