def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0, -10**18)
        for dx, dy, nx, ny in legal:
            v = -dist(nx, ny, ox, oy) - 0.2 * dist(nx, ny, cx, cy) - 0.001 * (nx + ny)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    # Choose a resource to race for: prefer those where we're at least as close as opponent.
    best_target = None
    best_rscore = -10**18
    for rx, ry in res:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # If we're closer (or tied), boost; else penalize.
        rscore = (1.5 if ds <= do else -1.0) * (10 - ds) + (0.4 if do <= ds else 0.0) * (10 - do) - 0.002 * (rx + ry)
        if rscore > best_rscore:
            best_rscore = rscore
            best_target = (rx, ry)

    tx, ty = best_target
    # Also consider denying: if opponent is heading to some resource, slightly move to reduce their progress.
    opp_best = None
    opp_best_do = 10**9
    for rx, ry in res:
        do = dist(ox, oy, rx, ry)
        if do < opp_best_do:
            opp_best_do = do
            opp_best = (rx, ry)
    ax, ay = opp_best

    best = (0, 0, -10**18)
    for dx, dy, nx, ny in legal:
        ds_now = dist(nx, ny, tx, ty)
        do_now = dist(nx, ny, ox, oy)
        ds_prev = dist(sx, sy, tx, ty)
        # Main objective: reduce our distance to target; secondary: keep away from opponent and deny their target.
        v = 3.0 * (ds_prev - ds_now) - 0.05 * ds_now - 0.5 * dist(nx, ny, ax, ay) + 0.15 * dist(nx, ny, ox, oy)
        # Avoid stepping into positions that give opponent immediate capture: if we move closer to their target than they are to it.
        if dist(nx, ny, ax, ay) + dist(ox, oy, ax, ay) < dist(sx, sy, ax, ay) + dist(ox, oy, ax, ay):
            v -= 0.3
        if v > best[2]:
            best = (dx, dy, v)

    return [best[0], best[1]]