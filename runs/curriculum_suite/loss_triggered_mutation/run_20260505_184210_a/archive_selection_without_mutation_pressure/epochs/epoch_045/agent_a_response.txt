def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal_self = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal_self.append((dx, dy))
    if not legal_self:
        return [0, 0]

    if not resources:
        # Go to center deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        def md(a, b, c, d):
            x = a - c
            if x < 0: x = -x
            y = b - d
            if y < 0: y = -y
            return x + y
        best, bestv = legal_self[0], None
        for dx, dy in legal_self:
            nx, ny = sx + dx, sy + dy
            v = md(nx, ny, cx, cy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    legal_opp = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal_opp.append((dx, dy))
    if not legal_opp:
        legal_opp = [(0, 0)]

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    def opp_next_min_dist(tx, ty):
        best = None
        for dx, dy in legal_opp:
            nx, ny = ox + dx, oy + dy
            v = man(nx, ny, tx, ty)
            if best is None or v < best:
                best = v
        return best

    # Strategic change: choose move that creates the largest "interception advantage"
    # by assuming opponent moves toward the same contested resource next turn.
    best_move = None
    best_score = None
    for dx, dy in legal_self:
        nx, ny = sx + dx, sy + dy
        # For each resource, compute how much closer we become than opponent after their move.
        # Score combines: (opp_next_dist - self_next_dist), preference for resources we can reach soon.
        local_best = None
        for rx, ry in resources:
            self_next = man(nx, ny, rx, ry)
            opp_next = opp_next_min_dist(rx, ry)
            # Strongly favor making opp_next worse than our next (intercept/deny).
            advantage = opp_next - self_next
            # Tie-break: prefer smaller self_next and also prefer disrupting closer-to-me resources.
            val = (advantage, -self_next, man(nx, ny, (w - 1) // 2, (h - 1) // 2))
            if local_best is None or val > local_best:
                local_best = val
        if best_score is None or local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]