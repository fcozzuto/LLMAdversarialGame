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
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if valid(x + dx, y + dy):
                c += 1
        return c
    def edge_bias(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)  # larger means more central

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny)
        mob = mobility(nx, ny)
        eb = edge_bias(nx, ny)

        if i_am_evader:
            # evader: maximize distance, prefer cornering (smaller edge_bias), keep mobility
            val = d * 5 + (0 if mob == 0 else mob) * 1.2 - eb * 1.0
        else:
            # pursuer: minimize distance, prefer mobility, avoid getting stuck near center if needed
            val = -d * 5 + (0 if mob == 0 else mob) * 1.2 + (eb * 0.1)

        if best_val is None or (val > best_val) or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move