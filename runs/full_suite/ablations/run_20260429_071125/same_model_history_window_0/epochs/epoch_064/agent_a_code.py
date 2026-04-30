def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev (diagonal-friendly)

    def best_target():
        if not resources:
            # No resources: drift toward opponent slightly to potentially block
            return (ox, oy)
        best = None
        best_key = None
        for r in resources:
            d_m = dist((sx, sy), r)
            d_o = dist((ox, oy), r)
            key = (d_o - d_m, -d_m)  # contest if we are closer; else pick closest
            if best_key is None or key > best_key:
                best_key = key
                best = r
        return best

    tx, ty = best_target()

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best_score = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        my_d = dist((nx, ny), (tx, ty))
        opp_d = dist((ox, oy), (tx, ty))
        # Prefer reducing distance to target; break ties by increasing opponent distance to target.
        score = (-my_d) + 0.15 * (opp_d - dist((ox, oy), (tx, ty)))
        # If target is likely contested, try to avoid stepping away from it.
        score += 0.05 * (dist((sx, sy), (tx, ty)) - my_d)
        # If we're stuck, bias toward moving closer to the opponent corner.
        score += 0.02 * (dist((ox, oy), (0, 0)) - dist((nx, ny), (0, 0)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]