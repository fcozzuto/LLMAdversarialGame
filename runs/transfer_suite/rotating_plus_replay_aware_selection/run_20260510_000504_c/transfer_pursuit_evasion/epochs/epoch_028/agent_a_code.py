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

    def dist2(x, y, a=ox, b=oy):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if valid(x + dx, y + dy):
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_score(x, y):
        best = -10**9
        for cx, cy in corners:
            best = max(best, dist2(x, y, cx, cy))
        return best

    best_dxdy = (0, 0)
    if i_am_evader:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny)  # maximize
            mob = mobility(nx, ny)
            cs = corner_score(nx, ny)
            val = (d, mob, cs)
            if best is None or val > best:
                best = val
                best_dxdy = (dx, dy)
    else:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny)  # minimize
            mob = mobility(nx, ny)
            val = (-d, mob, corner_score(nx, ny))
            if best is None or val > best:
                best = val
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]