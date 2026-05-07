def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Drift toward own corner diagonal inward to reduce being stuck behind obstacles.
        tx, ty = 3, 3 if (sx + sy) < (ox + oy) else 4
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # One-step lookahead: pick move that maximizes "resource contest" advantage.
    best = None
    best_val = -10**18
    for mv in moves:
        mx, my = sx + mv[0], sy + mv[1]
        if not legal(mx, my):
            continue

        # Evaluate up to a few nearest resources for speed.
        scored = []
        for rx, ry in resources:
            d_self = cheb(mx, my, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; also avoid letting opponent improve too much.
            # Add a small bias for resources nearer to current self to keep trajectory consistent.
            val = (d_opp - d_self) * 100 - d_self
            # Break ties deterministically by coordinates.
            val -= (rx * 0.001 + ry * 0.0001)
            scored.append((val, rx, ry, d_self, d_opp))
        scored.sort(reverse=True, key=lambda t: (t[0], -t[1], -t[2]))
        top = scored[:4]

        # Aggregate: maximize best contest target, but penalize moves that move us away from overall opportunities.
        best_contest = top[0][0]
        avg_self = 0
        avg_opp = 0
        for t in top:
            avg_self += t[3]
            avg_opp += t[4]
        n = len(top)
        avg_self //= n
        avg_opp //= n
        total = best_contest * 10 + (avg_opp - avg_self) * 3

        if total > best_val:
            best_val = total
            best = mv

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]