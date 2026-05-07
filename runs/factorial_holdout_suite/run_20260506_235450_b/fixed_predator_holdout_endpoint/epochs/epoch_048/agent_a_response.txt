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

    # Pick target deterministically: prefer resources where we can arrive no later; otherwise race earliest.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        adv = op_d - my_d  # positive means we can arrive earlier or same time
        if adv >= 0:
            key = (0, -adv, my_d, rx, ry)  # win-capable: biggest advantage, then nearest
        else:
            key = (1, op_d, my_d, rx, ry)   # race: smallest opponent arrival time
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    tx, ty = best[1]

    # Move choice: best next cell for collecting target while not stepping into obstacles.
    best_m = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine effect: invalid => stay
            dx, dy = 0, 0
        my_next = cheb(nx, ny, tx, ty)
        op_d_to_target = cheb(ox, oy, tx, ty)
        # Prefer decreasing our distance; if tied, prefer increasing opponent distance to target; then prefer move that keeps us closer overall.
        key = (my_next, op_d_to_target - my_next, -cheb(nx, ny, ox, oy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_m = [dx, dy]

    return best_m