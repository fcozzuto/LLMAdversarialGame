def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

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

    adj8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    def risk(x, y):
        r = 0
        if (x, y) in obst:
            return 10**6
        for dx, dy in adj8:
            if (x+dx, y+dy) in obst:
                r += 1
        return r

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Move away from nearest obstacle-adjacent cell if no resources.
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -risk(nx, ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    for dx, dy, nx, ny in legal:
        dme = 10**9
        dam = 10**9
        target_adv = -10**9
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we're competitive (smaller dm), and where opponent is farther.
            val = (-dm) + 0.85 * do
            if val > target_adv:
                target_adv = val
                dme, dam = dm, do
        v = target_adv - 0.6 * risk(nx, ny)
        # Small bias to actually reduce distance to best resource.
        v -= 0.02 * dme
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]