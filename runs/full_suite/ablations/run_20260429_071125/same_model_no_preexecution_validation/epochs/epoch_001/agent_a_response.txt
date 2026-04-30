def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Chebyshev distance works well for diagonal moves
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Choose target resource deterministically: nearest, then lexicographically
    if resources:
        target = min(resources, key=lambda r: (dist((sx, sy), r), r[0], r[1]))
    else:
        # If no resources, head toward opponent to contest
        target = (ox, oy)

    best_moves = []
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d_t = dist((nx, ny), target)
            d_o = dist((nx, ny), (ox, oy))
            # Prefer reducing distance to target; also prefer staying away from opponent
            score = (d_t, -d_o, nx, ny)
            if best_score is None or score < best_score:
                best_score = score
                best_moves = [(dx, dy)]
            elif score == best_score:
                best_moves.append((dx, dy))

    # Deterministic tie-break
    if best_moves:
        return list(min(best_moves, key=lambda m: (m[0], m[1])))
    return [0, 0]