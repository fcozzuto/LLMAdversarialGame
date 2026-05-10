def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    role = observation.get("self_role", "pursuer")

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_blocked(x, y):
        return (x, y) in obstacles

    corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))

    # Deterministic candidate order: prefer diagonals, then axis, then stay.
    deltas = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        if role == "pursuer":
            # Minimize distance; slightly prefer corners to encourage cornering.
            corner_bias = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            score = d * 1000 + corner_bias
            if best is None or score < best_score:
                best, best_score = (dx, dy), score
        else:
            # Evader: maximize distance; prefer farthest corner from pursuer.
            far_corner = max(abs(cx - ox) + abs(cy - oy) for cx, cy in corners)
            score = -d * 1000 + (far_corner - (min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)))
            if best is None or score > best_score:
                best, best_score = (dx, dy), score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]