def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))
    res_set = set(resources)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def nearest_dist(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    if not resources:
        tx = w - 1 if ox < w - 1 else 0
        ty = h - 1 if oy < h - 1 else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obs:
            return [dx, dy]
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [ddx, ddy]
        return [0, 0]

    opp_near = nearest_dist(ox, oy)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        on_res = 1 if (nx, ny) in res_set else 0
        my_near = nearest_dist(nx, ny)
        # Encourage grabbing, then staying closer than opponent to remaining resources.
        val = 0
        val += 100000 * on_res
        val += 250 * (opp_near - my_near)
        # Mild preference to reduce distance to opponent (keeps pressure deterministic).
        val -= 10 * cheb(nx, ny, ox, oy)
        # Avoid stepping into squares adjacent to many obstacles (deterministic local penalty).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    adj_obs += 1
        val -= 2 * adj_obs

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]