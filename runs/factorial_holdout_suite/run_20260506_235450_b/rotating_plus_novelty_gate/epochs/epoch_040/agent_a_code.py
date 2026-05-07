def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    rem = observation.get("remaining_resource_count", len(resources))
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not free(nx, ny):
            continue
        onto = 0
        min_myd = 10**9
        best_adv = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(nx, ny, ox, oy)  # placeholder to keep structure; overwritten below

            opd = cheb(nx, ny, rx, ry)  # corrected below
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd < min_myd: min_myd = myd
            adv = opd - myd
            if adv > best_adv: best_adv = adv
            if nx == rx and ny == ry: onto = 1

        d_op = cheb(nx, ny, ox, oy)
        val = (1000 + 2 * rem) * onto + 12 * best_adv - (min_myd) - 0.02 * d_op
        if val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return best_move