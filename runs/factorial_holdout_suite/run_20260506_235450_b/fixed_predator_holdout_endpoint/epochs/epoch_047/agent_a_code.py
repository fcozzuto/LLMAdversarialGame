def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

    if not resources:
        return [0, 0]

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_t = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        if my_d <= op_d:
            key = (0, my_d, rx, ry)  # win-capable: go for nearest
        else:
            key = (1, op_d, my_d, rx, ry)  # race: take what's being grabbed soon
        if best_key is None or key < best_key:
            best_key, best_t = key, (rx, ry)

    tx, ty = best_t
    best_m = (0, 0)
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        new_my = cheb(nx, ny, tx, ty)
        new_op = cheb(nx, ny, ox, oy)
        my_now = cheb(sx, sy, tx, ty)
        op_now = cheb(ox, oy, tx, ty)
        # Prefer reducing target distance; then increase relative advantage vs opponent on target
        rel = (op_now - new_my) - (op_now - my_now)
        key = (new_my, -rel, cheb(nx, ny, ox, oy), nx, ny)
        if best_k is None or key < best_k:
            best_k, best_m = key, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]