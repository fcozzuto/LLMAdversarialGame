def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_t = resources[0]
    best_diff = -10**18
    for rx, ry in resources:
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        diff = od - sd
        val = diff * 100 - sd
        if val > best_diff:
            best_diff = val
            best_t = (rx, ry)

    tx, ty = best_t
    oppd = king_dist(ox, oy, tx, ty)

    cx, cy = gw // 2, gh // 2
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd2 = king_dist(nx, ny, tx, ty)
        s = (oppd - sd2) * 100 - sd2
        # Tie-breaker: drift toward center slightly to reduce pathing traps
        s -= king_dist(nx, ny, cx, cy) * 0.1
        if s > best_s:
            best_s = s
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]