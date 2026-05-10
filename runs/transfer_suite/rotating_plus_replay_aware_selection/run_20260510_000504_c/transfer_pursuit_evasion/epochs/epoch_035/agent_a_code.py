def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    resources = observation.get("resources", []) or []
    target = None
    best_d = None
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
        except:
            continue
        d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        if best_d is None or d < best_d:
            best_d = d
            target = (rx, ry)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if target is None:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t = dist2(nx, ny, target[0], target[1])
        d_o = dist2(nx, ny, ox, oy)
        score = -d_t + 0.05 * d_o
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if not valid(sx + best_move[0], sy + best_move[1]):
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]