def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_r = None
    best_key = None
    for rx, ry in resources:
        if not valid(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; otherwise still pick the "least bad" one.
        if do < ds:
            key = (0, -(do - ds), rx, ry)  # negative gap => closer to unreachable but deterministic
        else:
            key = (1, (ds - do), rx, ry)   # primary: we win the race; secondary: smaller ds-do
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    best_step = (0, 0)
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Deterministic: minimize distance to target; if tie, maximize distance from opponent.
        key = (d_to, -d_opp, nx, ny)
        if best is None or key < best:
            best = key
            best_step = (dx, dy)

    return [best_step[0], best_step[1]]