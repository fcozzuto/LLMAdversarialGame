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
    evader = self_is_evader or (not opp_is_evader)  # if opponent isn't an evader, likely we are

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def wall_pen(x, y):
        d = x
        if y < d: d = y
        t = (w - 1) - x
        if t < d: d = t
        t = (h - 1) - y
        if t < d: d = t
        return -0.10 * d  # prefer staying away from edges

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

    best_move = [0, 0]
    if evader:
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d2 = dist2(nx, ny)
            score = d2 + 0.6 * mobility(nx, ny) + wall_pen(nx, ny)
            # also slightly discourage aligning directly with opponent to avoid wall-run capture lines
            if nx == ox or ny == oy:
                score -= 0.05
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d2 = dist2(nx, ny)
            score = -d2 + 0.4 * mobility(nx, ny) + wall_pen(nx, ny)
            # chase in a way that tends to reduce both axes (cutting off corners)
            score -= 0.02 * (abs(nx - ox) + abs(ny - oy))
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move