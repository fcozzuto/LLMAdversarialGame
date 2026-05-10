def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()

    i_am_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    if not ("purs" in self_role or "chase" in self_role):
        # If role field is unclear, infer: if opponent looks like pursuer, assume we are evader.
        if ("purs" in opp_role) or ("chase" in opp_role):
            i_am_evader = True
        elif ("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role):
            i_am_evader = False

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    # Corners are strong deterministic attractors for evasion in empty-ish boards.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_score(x, y, sign):
        best = -10**18
        for cx, cy in corners:
            v = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if v > best:
                best = v
        return sign * best

    # Penalize stepping adjacent to obstacles to avoid getting funneled.
    def obstacle_adj_penalty(x, y):
        if not obstacles:
            return 0
        p = 0
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                p += 1
        return p

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best_move = (0, 0)
    if i_am_evader:
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny)
            score = d + 0.25 * corner_score(nx, ny, 1) + 0.8 * mobility(nx, ny) - 2.0 * obstacle_adj_penalty(nx, ny)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        best_score = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny)
            # Chase while avoiding obstacle adjacency slightly.
            score = d - 0.15 * mobility(nx, ny) + 1.8 * obstacle_adj_penalty(nx, ny)
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]