def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    def mdist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = -10**18
    best_selfd = 10**9
    best_opd = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Evaluate "gain" over opponent for the best contested resource.
        self_best = 10**9
        opp_best = 10**9
        gain_best = -10**18

        for rx, ry in resources:
            ds = mdist(nx, ny, rx, ry)
            do = mdist(ox, oy, rx, ry)
            if ds < self_best:
                self_best = ds
            if do < opp_best:
                opp_best = do
            gain = do - ds  # positive means you are closer than opponent at this step
            if gain > gain_best:
                gain_best = gain

        # Primary: maximize gain_best; Secondary: minimize self_best; Tertiary: maximize opp_best proximity disadvantage.
        val = gain_best * 1000 - self_best
        if val > best_val or (val == best_val and self_best < best_selfd) or (val == best_val and self_best == best_selfd and opp_best < best_opd):
            best_val = val
            best_move = (dx, dy)
            best_selfd = self_best
            best_opd = opp_best

    return [int(best_move[0]), int(best_move[1])]