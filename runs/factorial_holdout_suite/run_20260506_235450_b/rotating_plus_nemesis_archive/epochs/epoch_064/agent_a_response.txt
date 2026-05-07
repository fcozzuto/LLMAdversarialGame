def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b):
        # Chebyshev distance matches king-like movement
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_value(nx, ny):
        if not resources:
            tx, ty = w // 2, h // 2
            return -dist((nx, ny), (tx, ty))

        # Choose the resource where we can get ahead the most (race condition).
        best = -10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d_self = dist((nx, ny), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # Prefer actions that reduce our time and increase opponent's time.
            # Add small deterministic tie-break based on coordinates.
            adv = (d_opp - d_self)
            # If we're at/adjacent in chebyshev, prioritize heavily.
            near_bonus = 5 if d_self <= 1 else 0
            val = 1000 * adv + near_bonus * 10 - (rx * 0.01 + ry * 0.001)
            if val > best:
                best = val
        return best

    best_move = [0, 0]
    best_score = -10**18
    # Deterministic iteration order: already fixed by moves list
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        sc = cell_value(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = [mx, my]

    return best_move