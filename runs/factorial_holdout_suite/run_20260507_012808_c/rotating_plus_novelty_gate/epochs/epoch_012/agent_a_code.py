def choose_move(observation):
    w = observation.get("grid_width")
    h = observation.get("grid_height")
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    if not resources or w is None or h is None:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = do - ds  # positive => I am closer
        key = (-score, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_step = None
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        nd = cheb(nx, ny, tx, ty)
        key = (nd, dx, dy)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = [dx, dy]

    return best_step if best_step is not None else [0, 0]