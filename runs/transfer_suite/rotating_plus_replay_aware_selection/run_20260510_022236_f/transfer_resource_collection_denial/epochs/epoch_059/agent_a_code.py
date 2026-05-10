def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    # Choose best target: prefer resources we can reach strictly before opponent; then maximize lead, then minimize our distance.
    best = None
    best_key = None
    for tx, ty in res:
        d_self = cheb(sx, sy, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Key: lead to opponent (larger better), then our distance (smaller better), then deterministic by coords
        key = (d_opp - d_self, -d_self, -tx, -ty)  # maximize lead, then minimize d_self
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Score candidate move: must be valid; prefer reducing distance to target; avoid obstacles and steer away from near-obstacles.
    def obstacle_proximity_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                nx, ny = x + ax, y + ay
                if (nx, ny) in obs:
                    pen += 1
        return pen

    best_move = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d_now = cheb(nx, ny, tx, ty)
        d_prev = cheb(sx, sy, tx, ty)
        # Prefer improvement; if equal, prefer fewer obstacle proximities; then deterministic by move order
        improve = d_prev - d_now
        pen = obstacle_proximity_pen(nx, ny)
        key = (improve, -pen, -abs(nx - tx), -abs(ny - ty), dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move