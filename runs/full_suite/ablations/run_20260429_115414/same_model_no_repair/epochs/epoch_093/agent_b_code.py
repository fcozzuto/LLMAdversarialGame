def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    best_t = None
    best_a = None
    best_md = 10**9
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        a = od - md
        if best_t is None or a > best_a or (a == best_a and md < best_md):
            best_t, best_a, best_md = (rx, ry), a, md
    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        opnd = cheb(ox, oy, nx, ny)
        key = (myd, opnd)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_key is None:
        return [0, 0]
    return best_move