def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_move = [0, 0]
    best_tie = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        best_for_move = None
        best_drs = None
        for rx, ry in res:
            drs = md(nx, ny, rx, ry)
            dro = md(ox, oy, rx, ry)
            # Prefer resources we approach quickly while the opponent is relatively far.
            sc = (-drs) + 0.6 * dro
            if best_for_move is None or sc > best_for_move or (sc == best_for_move and drs < best_drs):
                best_for_move = sc
                best_drs = drs

        # Global tie-breaker: smaller our distance to the chosen target.
        if best_score is None or best_for_move > best_score or (best_for_move == best_score and best_drs < best_tie):
            best_score = best_for_move
            best_move = [dx, dy]
            best_tie = best_drs

    return [int(best_move[0]), int(best_move[1])]