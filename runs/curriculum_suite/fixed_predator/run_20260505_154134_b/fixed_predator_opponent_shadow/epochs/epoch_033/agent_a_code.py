def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obs

    resources = [(int(x), int(y)) for (x, y) in resources if isinstance(x, (int, float)) and isinstance(y, (int, float))]
    best_t = None
    best_key = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        key = (od - sd, -sd, cx, cy)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (cx, cy)

    if best_t is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_t

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        if not valid_move(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        score = (od - sd, -sd, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]