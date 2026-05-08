def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = {(int(a), int(b)) for a, b in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)

    def min_obst_dist(x, y):
        best = 999
        for (ax, ay) in obs:
            d = ax - x
            if d < 0: d = -d
            e = ay - y
            if e < 0: e = -e
            md = d + e
            if md < best:
                best = md
        return best if best != 999 else 9

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)
        md = min_obst_dist(nx, ny)

        if is_evader:
            # Run from pursuer while staying mobile and not pressing into walls/obstacles.
            val = (dist * 10.0) + (fn * 1.5) - (md * 0.25)
        else:
            # Chase pursuer position while avoiding getting boxed in.
            val = (-dist * 10.0) + (fn * 1.5) - (md * 0.05)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]