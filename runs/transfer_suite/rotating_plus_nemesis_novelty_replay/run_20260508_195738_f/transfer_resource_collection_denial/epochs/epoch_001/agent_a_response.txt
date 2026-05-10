def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        # Target nearest resource by Chebyshev distance (diagonal-friendly)
        best = None
        for rx, ry in resources:
            d = max(abs(rx - sx), abs(ry - sy))
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources visible: drift toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    # Deterministic order preference
    moves.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    def dist(x, y, a, b):
        return max(abs(a - x), abs(b - y))

    cur_d = dist(sx, sy, tx, ty)
    best_move = None
    best_score = None
    for dx, dy, nx, ny in moves:
        d = dist(nx, ny, tx, ty)
        # Prefer strictly closer; if tied, prefer closer to opponent (disrupt) slightly; then lexicographic
        score = (0 if d < cur_d else 1, d, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
        if d < cur_d:
            # Keep searching for even better deterministic score, but ensure not stuck
            pass

    return best_move if best_move is not None else [0, 0]