def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if res:
        best_r = None
        best_val = None
        for x, y in res:
            d1 = dist(sx, sy, x, y)
            d2 = dist(ox, oy, x, y)
            val = d1 - 0.75 * d2  # prefer closer resources that are farther for opponent
            if best_val is None or val < best_val or (val == best_val and d1 < dist(sx, sy, best_r[0], best_r[1])):
                best_val = val
                best_r = (x, y)
        tx, ty = best_r
        best_move = [0, 0]
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            s_to = dist(nx, ny, tx, ty)
            o_to = dist(nx, ny, ox, oy)
            step_score = s_to - 0.15 * o_to  # slight safety bias
            if best_score is None or step_score < best_score:
                best_score = step_score
                best_move = [dx, dy]
        return [int(best_move[0]), int(best_move[1])]

    # No resources visible: drift to reduce opponent influence; prefer increasing distance and centrality
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_away = dist(nx, ny, ox, oy)
        center = dist(nx, ny, (w - 1) // 2, (h - 1) // 2)
        # maximize distance from opponent, tie-break by going towards center
        score = -d_away + 0.05 * center
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]