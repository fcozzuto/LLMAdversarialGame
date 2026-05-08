def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_adv(px, py):
        if not resources:
            return -10**9, 0
        best = (-10**18, 10**9)
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer (earlier)
            # prefer larger adv, then closer target for us, then deterministic
            if adv > best[0] or (adv == best[0] and (ds < best[1])):
                best = (adv, ds)
        return best

    # If no resources, move to reduce distance to opponent (deterministic "interferer")
    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v < best[0] or (v == best[0] and (nx, ny) < (best[1], best[2])):
                best = (v, nx, ny)
        return [best[1] - sx, best[2] - sy]

    cur_adv, cur_ds = best_adv(sx, sy)
    best_move = (0, 0)
    best_val = (-10**18, 10**18, (0, 0))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        adv, ds = best_adv(nx, ny)
        # prefer strictly improving adv; otherwise improve ds; then lexicographic move
        delta = adv - cur_adv
        val = (delta, -ds, (dx, dy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]