def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    ox, oy = observation["opponent_position"]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # roam deterministically: head to corner farthest from opponent in Chebyshev metric
        corners = [(0, 0), (w - 1, h - 1), (0, h - 1), (w - 1, 0)]
        best_corner = None
        best_val = None
        for cx, cy in corners:
            v = cheb(sx, sy, cx, cy) + 0.01 * cheb(ox, oy, cx, cy)
            if best_val is None or v > best_val:
                best_val = v
                best_corner = (cx, cy)
        cx, cy = best_corner
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        for ddx, ddy, _, _ in legal:
            if ddx == dx and ddy == dy:
                return [ddx, ddy]
        return [legal[0][0], legal[0][1]]

    # choose target resource where we are relatively closer than opponent
    best_target = resources[0]
    best_priority = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        priority = (my_d - op_d, my_d, rx + 31 * ry)
        if best_priority is None or priority < best_priority:
            best_priority = priority
            best_target = (rx, ry)
    tx, ty = best_target

    # pick move that improves target and also prevents conceding immediately to opponent
    best_move = (0, 0, sx, sy)
    best_score = None
    for dx, dy, nx, ny in legal:
        my_d_next = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        # if opponent already closer, prioritize contesting by reducing our distance sharply
        score = (my_d_next - op_d, my_d_next, (nx + 17 * ny), 0)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]