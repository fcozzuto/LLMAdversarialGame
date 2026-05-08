def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            cand = (-v, nx, ny)  # maximize distance from opponent
            if best is None or cand < best:
                best = cand
        return [best[2] - sx, best[1] - sy]

    # Choose a contested resource: high (opp_dist - self_dist), prefer closer to self among ties.
    best_t = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = od - sd
        cand = (-val, sd, rx, ry)  # maximize val, minimize sd
        if best_t is None or cand < best_t:
            best_t = cand
    _, _, tx, ty = best_t

    # Move to reduce distance to chosen target; if equal, prefer increasing distance for opponent (denial).
    best_m = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        my_now = cheb(sx, sy, tx, ty)
        my_next = cheb(nx, ny, tx, ty)
        opp_now = cheb(ox, oy, tx, ty)
        # Denial proxy: after our move, assume opponent next step can be worse if they are "pushed" off target region
        # by moving away from opponent along cheb metric to target.
        opp_next_proxy = cheb(ox, oy, nx, ny)
        cand = (my_next - my_now, opp_now - opp_next_proxy, nx, ny)
        if best_m is None or cand < best_m:
            best_m = cand

    return [best_m[2] - sx, best_m[3] - sy]