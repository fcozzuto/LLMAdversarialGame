def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): nx, ny = sx, sy
            d = cheb(nx, ny, ox, oy)
            if d > best[2] or (d == best[2] and (dx, dy) < (best[0], best[1])):
                best = (dx, dy, d)
        return [best[0], best[1]]

    # Choose resource where we arrive no later than opponent; tie-break by biggest lead then closeness.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        key = (-(lead > 0), -lead, ds, rx, ry)  # prefer lead>0, then larger lead, then closer, deterministic
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Move to reduce distance to target; also avoid getting too close when opponent is about to contest.
    opp_dist_now = cheb(sx, sy, ox, oy)
    contesting = (cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty))

    best = (0, 0, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): nx, ny = sx, sy
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Primary: minimize distance to target (encode as max negative)
        score = -d_to * 100
        if contesting:
            score += d_opp  # when contesting, keep some separation deterministically
        else:
            score += (d_opp // 2)
        if score > best[2] or (score == best[2] and (dx, dy) < (best[0], best[1])):
            best = (dx, dy, score)

    return [best[0], best[1]]