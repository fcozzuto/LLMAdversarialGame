def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x, y, tx, ty):
        dx = x - tx
        if dx < 0: dx = -dx
        dy = y - ty
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def obstacle_pressure(x, y):
        # lower is better
        c = 0
        for nx in (x - 1, x, x + 1):
            if nx < 0 or nx >= w:
                continue
            for ny in (y - 1, y, y + 1):
                if ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obs:
                    c += 1
        return c

    def corner_bias(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # prefer corners farthest from opponent (for evader) or closest (for pursuer)
        best = None
        for cx, cy in corners:
            d = cheb(cx, cy, ox, oy)
            if best is None:
                best = d
            else:
                if is_evader and d > best:
                    best = d
                elif (not is_evader) and d < best:
                    best = d
        # how close we are to the desired corner class
        # (approx: use distance to corners, with a deterministic tie-break)
        desired = None
        for cx, cy in corners:
            score = cheb(cx, cy, ox, oy)
            if is_evader:
                if desired is None or score > desired[0]:
                    desired = (score, cx, cy)
            else:
                if desired is None or score < desired[0]:
                    desired = (score, cx, cy)
        cx, cy = desired[1], desired[2]
        return cheb(x, y, cx, cy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        op = obstacle_pressure(nx, ny)
        cb = corner_bias(nx, ny)
        if is_evader:
            # maximize distance; avoid obstacles; move toward farthest-corner region
            val = (d * 1000) - (op * 10) - (cb * 2)
        else:
            # minimize distance; avoid obstacles; reduce cb (toward closest-corner region)
            val = (-d * 1000) - (op * 10) - (cb * 2)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]