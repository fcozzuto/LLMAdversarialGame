def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    opp_is_evader = ("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role)
    i_am_evader = self_is_evader or (not opp_is_evader)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if valid(x + dx, y + dy):
                c += 1
        return c

    def center_bias(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    best_val = None
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny)
        mob = mobility(nx, ny)
        cb = center_bias(nx, ny)
        far_corner = max((abs(nx - cx) + abs(ny - cy)) for cx, cy in corners)
        # Evader: maximize separation; additionally prefer lower mobility (to reduce escape routes for pursuer).
        # Pursuer: minimize separation; prefer higher mobility and centrality.
        if i_am_evader:
            val = d * 10 - mob * 2 + far_corner * 0.5 + cb * 0.1
        else:
            val = -d * 10 + mob * 2 + cb * 0.6 - far_corner * 0.05
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]