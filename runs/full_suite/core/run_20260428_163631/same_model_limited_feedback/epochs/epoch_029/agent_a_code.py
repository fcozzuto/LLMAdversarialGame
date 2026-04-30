def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev

    def best_resource():
        if not resources:
            return (w // 2, h // 2)
        best = None
        bs = None
        for r in resources:
            d1 = dist((sx, sy), r)
            d2 = dist((ox, oy), r)
            # Prefer resources closer to us, and deprioritize those closer to opponent.
            # Small deterministic tie-breaker by coordinates.
            score = (d1 - 0.9 * d2, r[0], r[1])
            if bs is None or score < bs:
                bs = score
                best = r
        return best

    tx, ty = best_resource()

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]
    best_move = None
    best_d = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), (tx, ty))
        # Prefer moves that reduce distance to target; lightly discourage moving away from opponent too much
        # to keep some pressure symmetry.
        opp_change = dist((nx, ny), (ox, oy))
        cand = (d, opp_change, dx, dy)
        if best_d is None or cand < best_d:
            best_d = cand
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move