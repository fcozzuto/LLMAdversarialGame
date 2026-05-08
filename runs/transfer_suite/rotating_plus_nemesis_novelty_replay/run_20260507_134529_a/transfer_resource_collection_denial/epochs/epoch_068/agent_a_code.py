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

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            cand = (-v, nx, ny, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[3], best[4]]

    # Choose the resource we can reach first compared to opponent; then maximize that advantage.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        best_for_move = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Maximize (od - sd). Tie-break: smaller sd, then lexicographic target.
            cand = (od - sd, -sd, rx, ry)
            if best_for_move is None or cand > best_for_move:
                best_for_move = cand

        # Also keep a small preference for moving toward the best target to avoid dithering.
        tx, ty = best_for_move[2], best_for_move[3]
        tie_pref = cheb(nx, ny, tx, ty)
        score = (best_for_move[0], best_for_move[1], -tie_pref)
        cand2 = (score[0], score[1], score[2], nx, ny, dx, dy)
        if best is None or cand2 > best:
            best = cand2

    return [best[5], best[6]]