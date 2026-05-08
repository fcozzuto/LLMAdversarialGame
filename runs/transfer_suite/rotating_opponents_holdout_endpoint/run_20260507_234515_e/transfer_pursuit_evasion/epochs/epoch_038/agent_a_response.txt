def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    self_is_pursuer = ("purs" in role) or (role == "")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in oset

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def corner_score(x, y):
        return max(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    def predict_evader(px, py, ax, ay):
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            val = (dist(nx, ny, ax, ay), corner_score(nx, ny))
            if best_val is None or (val[0], val[1]) > best_val:
                best_val = (val[0], val[1])
                best = (dx, dy, nx, ny)
        if best is None:
            return px, py
        return best[2], best[3]

    if self_is_pursuer:
        ex, ey = predict_evader(ox, oy, sx, sy)
        best_move = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if nx == ox and ny == oy:
                return [dx, dy]
            key = (dist(nx, ny, ex, ey), dist(nx, ny, ox, oy), -(corner_score(nx, ny)))
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        best_move = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if nx == ox and ny == oy:
                continue
            key = (-dist(nx, ny, ox, oy), -corner_score(nx, ny))
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]