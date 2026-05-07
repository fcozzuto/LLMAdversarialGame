def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    resources_set = set((r[0], r[1]) for r in resources)

    def clamp(x, y):
        return (x, y) if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles else (sx, sy)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # If no resources visible, move toward center with mild bias away from opponent.
    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = clamp(sx + dx, sy + dy)
            dself = man(nx, ny, tx, ty)
            do = man(nx, ny, ox, oy)
            key = (dself - 0.05 * do, dself, nx, ny)
            if key < best:
                best = key
                bx, by = nx, ny
        return [bx - sx, by - sy]

    # One-step lookahead: choose move maximizing (opp_nearest - self_nearest) and prefer grabbing.
    best_key = (10**18, 0, 0, 0)
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = clamp(sx + dx, sy + dy)

        self_gain = 1 if (nx, ny) in resources_set else 0
        opp_gain = 1 if (ox, oy) in resources_set else 0

        # Nearest remaining resource distances from next positions.
        self_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            # Consider resource "captured" if we move onto it; otherwise it's still available.
            if (rx, ry) == (nx, ny):
                continue
            d = man(nx, ny, rx, ry)
            if d < self_best: self_best = d
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if (rx, ry) == (ox, oy):
                # opponent could collect immediately, but we only have our move;
                # keep as distance 0 to reflect urgency.
                opp_best = 0
                break
            d = man(ox, oy, rx, ry)
            if d < opp_best: opp_best = d

        if self_best == 10**9:
            self_best = 0
        if opp_best == 10**9:
            opp_best = 0

        # Key: big advantage in keeping opponent away; also prefer closer self and deterministic coord tie.
        adv = (opp_best - self_best) + 3 * self_gain - 1 * opp_gain
        key = (-adv, self_best, -(dx == 0 and dy == 0), nx, ny)
        if key < best_key:
            best_key = key
            best_move = [nx - sx, ny - sy]

    return best_move