def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]
    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    # Choose a target that we are relatively closer to, while making it far from opponent
    if res:
        best_t = res[0]
        best_s = -10**18
        for x, y in res:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            # Prefer: self relatively closer; also consider absolute closeness
            s = 3 * (do - ds) - ds
            # If tie, bias upward/left deterministically (anti-oscillation)
            if s > best_s or (s == best_s and (x < best_t[0] or (x == best_t[0] and y < best_t[1]))):
                best_s = s
                best_t = (x, y)
        tx, ty = best_t

        # If opponent is already significantly closer, switch to a target where we win the contest
        min_ds = 10**9
        min_do = 10**9
        for x, y in res:
            min_ds = min(min_ds, cheb(sx, sy, x, y))
            min_do = min(min_do, cheb(ox, oy, x, y))
        if min_do - min_ds >= 2:
            best_t = res[0]
            best_s = -10**18
            for x, y in res:
                ds = cheb(sx, sy, x, y)
                do = cheb(ox, oy, x, y)
                s = 5 * (ds - do) - 0.5 * ds  # prefer places where opponent is not closer
                if s > best_s:
                    best_s = s
                    best_t = (x, y)
            tx, ty = best_t

        # Move that maximizes the same objective locally
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            ds2 = cheb(nx, ny, tx, ty)
            do2 = cheb(ox, oy, tx, ty)
            # we don't know opponent move; approximate by reducing our distance and increasing contest
            val = 3 * (do2 - ds2) - ds2
            # mild obstacle-avoidance: discourage adjacency to obstacles
            adj = 0
            for ox2, oy