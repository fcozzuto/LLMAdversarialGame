def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx + dy

    valid_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy))

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Prefer resources we can reach first; break ties by closeness to us, then fixed order.
            key = (myd - opd, myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    # Choose move that best reduces distance to target; secondarily avoids approaching opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        d_to_target = dist(nx, ny, tx, ty)
        # Encourage moving away from opponent slightly when not directly improving our target distance.
        d_to_opp = dist(nx, ny, ox, oy)
        score = (d_to_target, -d_to_opp, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]