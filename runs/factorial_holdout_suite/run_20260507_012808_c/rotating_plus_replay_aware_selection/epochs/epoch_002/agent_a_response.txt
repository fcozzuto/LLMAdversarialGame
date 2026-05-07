def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sign(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))

    cx, cy = w // 2, h // 2
    if not moves:
        return [0, 0]

    if resources:
        # Choose target resource with best relative advantage (lower is better)
        best_r = None
        best_key = None
        for rx, ry in resources:
            d1 = dist((sx, sy), (rx, ry))
            d2 = dist((ox, oy), (rx, ry))
            key = (d1 - d2, d1, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = cx, cy

    def opponent_next_pos(tx, ty):
        # Greedy one-step toward the target using same move constraints
        best = (ox, oy)
        best_d = dist((ox, oy), (tx, ty))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = ox + dx, oy + dy
                if inb(nx, ny):
                    d = dist((nx, ny), (tx, ty))
                    # break ties deterministically by position
                    if d < best_d or (d == best_d and (nx, ny) < best):
                        best_d = d
                        best = (nx, ny)
        return best

    opp_nx, opp_ny = opponent_next_pos(tx, ty)

    # If we are already on the target, don't move (unless obstacle rules changed; but inb ensures validity)
    if (sx, sy) == (tx, ty):
        return [0, 0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        self_d = dist((nx, ny), (tx, ty))
        opp_d = dist((opp_nx, opp_ny), (tx, ty))
        # Encourage capturing race; slight preference to move toward target and away from opponent when close
        close_bias = 0
        if dist((nx, ny), (ox, oy)) <= 2:
            close_bias = 0.01 * dist((nx, ny), (ox, oy))
        score = (self_d - opp_d, self_d, close_bias, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]