def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer strictly earlier; then closer; then more opponent delay; then stable tie-break
        key = (0 if ds < do else 1, ds, -do, rx, 7 * ry + rx)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # If no safe direct progress, still move to best heuristic neighbor.
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Favor reducing our distance; if we can beat opponent at/near arrival, prioritize that.
        win_flag = 0 if ds2 <= do2 else 1
        # Also slightly prefer moving to reduce opponent future reach (blocking by not being the one taking next turn).
        opp_to = cheb(nx, ny, ox, oy)
        step_safety = 0
        # tiny penalty for moving away from target too much
        key = (win_flag, ds2, -do2, abs(nx - tx) + abs(ny - ty), -opp_to, step_safety, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]