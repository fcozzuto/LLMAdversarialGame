def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = min(cand, key=lambda t: (cheb(t[2], t[3], tx, ty), t[0], t[1]))
        return [best[0], best[1]]

    # Select move that maximizes "capture advantage" over opponent for the best reachable resource.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in cand:
        move_best = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we reduce our distance and keep opponent farther.
            score = (od - sd, -sd, -(abs(rx - nx) + abs(ry - ny)))
            if move_best is None or score > move_best:
                move_best = score
        if move_best is None:
            continue
        if best_score is None or move_best > best_score:
            best_score = move_best
            best_move = (dx, dy, nx, ny)

    if best_move is None:
        best = min(cand, key=lambda t: (0, cheb(t[2], t[3], resources[0][0], resources[0][1])))
        return [best[0], best[1]]
    return [best_move[0], best_move[1]]