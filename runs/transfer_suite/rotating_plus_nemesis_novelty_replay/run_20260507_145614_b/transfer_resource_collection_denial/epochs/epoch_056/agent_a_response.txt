def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # If already on a resource, stay.
    for r in resources:
        if sx == r[0] and sy == r[1]:
            return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    # Determine for each resource which agent is closer (tie favors self via small bias).
    def best_competition_value(x, y):
        # Higher is better for self.
        best = -10**9
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Encourage grabbing resources where opponent is not closer, and reduce self distance.
            v = (od - sd) * 10 - sd
            if v > best:
                best = v
        return best

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Main: win the race to the same resource set.
        v = best_competition_value(nx, ny)
        # Secondary: move toward the currently best resource (to avoid oscillations).
        # Also, prefer cells with higher mobility to reduce being boxed.
        m = mobility(nx, ny)
        # Tertiary: deterministic tie-break by coordinates.
        candidates.append((v, m, -cheb(nx, ny, w // 2, h // 2), nx, ny, dx, dy))

    candidates.sort(reverse=True)
    if candidates:
        return [candidates[0][5], candidates[0][6]]

    return [0, 0]