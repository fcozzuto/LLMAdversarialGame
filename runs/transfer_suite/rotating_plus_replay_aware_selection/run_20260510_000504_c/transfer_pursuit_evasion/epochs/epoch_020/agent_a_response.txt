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

    def edge_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = dist2(nx, ny)
        mob = mobility(nx, ny)
        e = edge_dist(nx, ny)
        if i_am_evader:
            # Maximize distance, avoid getting cornered, keep mobility, and don't drift into obstacles/edges.
            val = (d2 * 1.2) + (mob * 0.35) + (e * 0.12) - 0.08 * (d2 - dist2(sx, sy))
        else:
            # Minimize distance, maintain mobility, and avoid edges where possible.
            val = (-d2 * 1.4) + (mob * 0.25) + (e * 0.06)
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best