def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources") or []

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_op = dist(nx, ny, ox, oy)
        nearest_res = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            nearest_res = min(nearest_res, dist(nx, ny, rx, ry))
        if nearest_res == 10**9:
            nearest_res = dist(nx, ny, (w - 1) // 2, (h - 1) // 2)
        score = -nearest_res + 0.05 * d_op
        # small deterministic tie-break: prefer staying on (or near) best_score direction
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]