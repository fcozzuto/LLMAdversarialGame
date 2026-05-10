def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = corners[0]
    best_corner_dist = -1
    for cx, cy in corners:
        d = cheb(x, y, cx, cy)
        if d > best_corner_dist:
            best_corner_dist = d
            corner = (cx, cy)

    cx, cy = corner
    best_opp = (ox, oy)
    best_opp_dist = None
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        if best_opp_dist is None or d < best_opp_dist:
            best_opp_dist = d
            best_opp = (nx, ny)

    px, py = best_opp

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        d_pred = cheb(nx, ny, px, py)
        d_now = cheb(nx, ny, ox, oy)
        val = (d_pred * 100 + d_now)  # prioritize reaching predicted position; then current
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]