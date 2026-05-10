def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or (not (("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role)))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def far_corner2(x, y):
        best = -10**18
        for cx, cy in corners:
            dx, dy = x - cx, y - cy
            v = dx * dx + dy * dy
            if v > best:
                best = v
        return best

    def near_obstacle(x, y):
        if not obstacles:
            return 0
        m = 10**18
        for bx, by in obstacles:
            d = (x - bx) * (x - bx) + (y - by) * (y - by)
            if d < m:
                m = d
        return 1 if m <= 2 else 0

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = dist2(nx, ny)
        mob = mobility(nx, ny)
        nb = near_obstacle(nx, ny)
        if i_am_evader:
            sc = d2 + 0.25 * far_corner2(nx, ny) + 0.2 * mob - 0.5 * nb
        else:
            sc = -d2 + 0.1 * mob - 0.2 * nb
        if best is None or sc > best or (sc == best and (dx, dy) < best_move):
            best, best_move = sc, (dx, dy)

    if not valid(sx, sy):
        return [0, 0]
    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]