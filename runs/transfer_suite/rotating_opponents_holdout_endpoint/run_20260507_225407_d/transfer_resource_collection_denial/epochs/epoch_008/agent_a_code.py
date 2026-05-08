def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_t = None
    best_sc = -10**18

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Beat bias: prefer targets where we arrive earlier; then closer.
        sc = (do - ds) * 2000 - ds * 6 + (do - ds) * (do > ds) * 50
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t
    if cheb(sx, sy, tx, ty) == 0:
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh:
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Encourage reducing our distance while keeping winning arrival advantage.
        val = (do2 - ds2) * 2100 - ds2 * 8
        # Mildly avoid drifting toward opponent when tie-ish.
        val += (cheb(ox, oy, nx, ny) - cheb(sx, sy, nx, ny)) * 2
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move