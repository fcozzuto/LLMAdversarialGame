def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    resources = [tuple(p) for p in (observation.get("resources") or [])]
    w1, h1 = w - 1, h - 1

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def open_count(x, y):
        c = 0
        for ax, ay in deltas:
            nx, ny = x + ax, y + ay
            if inb(nx, ny) and (nx, ny) not in obstacles:
                c += 1
        return c

    if resources:
        best_res = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we are closer
            key = (-(adv), ds, rx, ry)  # deterministic tie-break
            if best_key is None or key < best_key:
                best_key = key
                best_res = (rx, ry)
        rx, ry = best_res

        best_move = (0, 0)
        best_val = -10**18
        ds0 = cheb(sx, sy, rx, ry)
        do0 = cheb(ox, oy, rx, ry)
        for dx, dy, nx, ny in legal:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # chase target; strongly avoid moves that make us lose the race
            race_pen = 0
            if do <= ds:
                race_pen = (ds - do + 1) * 3.0
            val = -ds * 3.0 + (do - ds) * 1.2 - race_pen + 0.05 * open_count(nx, ny)
            # tiny preference for maintaining advantage vs starting
            val += (ds0 - ds) * 0.2 + (do0 - do) * 0.0
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        # no resources: move to corner that's farthest from opponent
        target = (0, 0)
        best_corner = None
        best_d = -1
        for cx, cy in [(0, 0), (0, h1), (w1, 0), (w1, h1)]:
            d = cheb(cx, cy, ox, oy)
            if d > best_d:
                best_d = d
                best_corner = (cx, cy)
        tx, ty = best_corner
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy, nx, ny in legal:
            val = -cheb(nx, ny, tx, ty) + 0.01 * open_count(nx, ny)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]