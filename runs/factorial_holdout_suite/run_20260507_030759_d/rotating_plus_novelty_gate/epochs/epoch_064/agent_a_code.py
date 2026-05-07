def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []
    resources = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    resset = set(resources)

    def legal_moves():
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    out.append((dx, dy))
        return out

    legal = legal_moves()
    if not legal:
        return [0, 0]

    if (sx, sy) in resset:
        return [0, 0]

    if not resources:
        # Drift toward the center to reduce being stuck
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def dist(a, b, c, d):
        ad = a - c
        bd = b - d
        return (ad * ad + bd * bd)

    best_move = None
    best_score = None
    # Score: prioritize getting to a resource quickly; then choose resources opponent is unlikely to reach quickly.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_for_move = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Lower is better for self, but larger opponent distance is better.
            score = sd - 0.7 * od
            if best_for_move is None or score < best_for_move:
                best_for_move = score
        if best_score is None or best_for_move < best_score:
            best_score = best_for_move
            best_move = (dx, dy)
        elif best_for_move == best_score:
            # Deterministic tie-break: prefer moves with smaller dx then smaller dy
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]