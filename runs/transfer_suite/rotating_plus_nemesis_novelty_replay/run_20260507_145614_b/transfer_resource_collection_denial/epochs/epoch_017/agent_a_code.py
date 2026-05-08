def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def target_priority(rx, ry):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # First preference: ensure we can arrive first; then earlier arrival; then larger advantage
        if ds <= do:
            return (0, ds, -(do - ds), rx, ry)
        # Otherwise strongly prefer targets opponent is worse at reaching
        return (1, do - ds, ds, rx, ry)

    best_r = None
    best_key = None
    for rx, ry in resources:
        if valid(rx, ry):
            k = target_priority(rx, ry)
            if best_key is None or k < best_key:
                best_key = k
                best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    best_step = (0, 0)
    best_step_key = None
    cur_ds = cheb(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Prefer reducing distance; if tie, prefer not giving opponent an earlier access advantage
        step_key = (nds, nds - cur_ds, ndo - nds, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]