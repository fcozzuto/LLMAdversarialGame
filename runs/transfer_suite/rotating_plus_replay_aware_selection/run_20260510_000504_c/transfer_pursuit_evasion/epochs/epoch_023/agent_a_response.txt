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
    def central(x, y):
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        return -((x - cx) * (x - cx) + (y - cy) * (y - cy))
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if valid(x + dx, y + dy):
                c += 1
        return c

    best = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny)
        mob = mobility(nx, ny)
        cent = central(nx, ny)
        if i_am_evader:
            val = d + 0.35 * cent + 0.25 * mob
            # small tie-breaker: prefer moves that don't reduce mob
            val += 0.02 * (mob if valid(nx, ny) else 0)
            better = (best_val is None) or (val > best_val)
        else:
            val = -d + 0.20 * mob + 0.05 * cent
            better = (best_val is None) or (val > best_val)
        if better:
            best_val = val
            best = [dx, dy]
    return best