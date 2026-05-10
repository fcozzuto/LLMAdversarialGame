def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if it is None:
            continue
        x, y = (it.get("x"), it.get("y")) if isinstance(it, dict) else (it[0], it[1])
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def opp_best_move(myx, myy, ex, ey):
        best = None
        bestd = -10**9
        for dx, dy in deltas:
            nx, ny = ex + dx, ey + dy
            if not valid(nx, ny):
                nx, ny = ex, ey
            d = dist(myx, myy, nx, ny)
            if d > bestd:
                bestd = d
                best = (nx, ny)
        return best

    best_move = (0, 0)
    best_score = 10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        pred_ex, pred_ey = opp_best_move(nx, ny, ox, oy)
        if pred_ex is None:
            pred_ex, pred_ey = ox, oy
        d1 = dist(nx, ny, pred_ex, pred_ey)

        # Tie-break: try to move toward the nearest edge to reduce opponent escape area.
        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        score = d1 * 100 - edge
        if score < best_score:
            best_score = score
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]