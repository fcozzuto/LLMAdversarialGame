def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer resources we can take (opp farther), otherwise ones to deny/intercept.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Higher is better: we want (od - sd) large; also break ties by closer to us.
        val = (od - sd, -sd, rx, ry)
        if best is None or val > best[0]:
            best = (val, rx, ry)
    _, tx, ty = best

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    # Deterministic ordering adjustment based on turn.
    turn = int(observation.get("turn_index", 0) or 0)
    start = turn % len(moves)
    moves = moves[start:] + moves[:start]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose best immediate move: minimize distance to target, but avoid obstacles.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = md(nx, ny, tx, ty)
        d_opp = md(nx, ny, tx, ty) - md(ox, oy, tx, ty)  # relative pressure heuristic
        score = (d1, d_opp, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves are blocked, deterministically stay.
    return best_move if best_score is not None else [0, 0]