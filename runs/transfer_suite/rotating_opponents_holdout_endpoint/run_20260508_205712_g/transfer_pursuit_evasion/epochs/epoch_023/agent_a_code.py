def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def adj_obst_pen(x, y):
        pen = 0
        for dx, dy in moves:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    def predict_opponent_next():
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not ok(nx, ny):
                continue
            dist = cheb(nx, ny, sx, sy)
            val = dist * 10 - adj_obst_pen(nx, ny)
            if val > best[1]:
                best = ((nx, ny), val)
        if best[0] is None:
            return (ox, oy)
        return best[0]

    pred_ox, pred_oy = predict_opponent_next()
    srole = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in srole) or ("chaser" in srole) or ("pursue" in srole)

    best_move = [0, 0]
    best_val = -10**18 if pursuer else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if pursuer:
            dist = cheb(nx, ny, pred_ox, pred_oy)
            val = -dist * 100 - adj_obst_pen(nx, ny) * 2
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            dist = cheb(nx, ny, pred_ox, pred_oy)
            val = dist * 100 - adj_obst_pen(nx, ny) * 2
            if val < best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]