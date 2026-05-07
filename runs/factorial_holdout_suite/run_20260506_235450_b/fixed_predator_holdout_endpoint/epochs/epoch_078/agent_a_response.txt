def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    t = int(observation.get("turns_remaining", 0) or 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal or not resources:
        return [0, 0]

    res_cells = []
    for r in resources:
        if len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                res_cells.append((x, y))
    if not res_cells:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        move_score = -10**18
        for rx, ry in res_cells:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # Prefer resources we can reach before opponent; otherwise, prioritize races we can still catch.
            favorable = self_d <= opp_d
            slack = opp_d - self_d
            # Small time-pressure: earlier collection is better.
            time_term = -(self_d + max(0, self_d - t) * 2)
            if favorable:
                s = 1000 + 50 * slack + time_term
            else:
                # If opponent is closer, only chase if we can reduce the gap meaningfully.
                s = -1000 + 20 * slack + time_term
            if s > move_score:
                move_score = s
        # If two moves lead to similar chase values, add a denial bias: avoid letting opponent get closer next.
        opp_closer_bias = md(ox, oy, nx, ny) - md(ox, oy, sx, sy)
        move_score -= 0.5 * opp_closer_bias
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]