def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or (
        not (("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role))
    )

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

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

    def corner_bias(x, y):
        best = -10**18
        for cx, cy in corners:
            dx, dy = x - cx, y - cy
            v = dx * dx + dy * dy
            if v > best:
                best = v
        return best

    best_move = (0, 0)
    best_val = -10**18 if i_am_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist2(nx, ny)
        m = mobility(nx, ny)
        cb = corner_bias(nx, ny)
        if i_am_evader:
            val = d + 0.7 * m + 0.001 * cb
            if val > best_val:
                best_val, best_move = val, (dx, dy)
        else:
            val = d - 0.7 * m - 0.001 * cb
            if val < best_val:
                best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]