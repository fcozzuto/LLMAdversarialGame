def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Deterministic move ranking: prefer moves that can reach a resource sooner than opponent
    best = None  # (score, -self_steps, rx, ry, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in resources:
            return [dx, dy]
        best_for_move = (-10**18, 10**18, 10**18, None)  # (lead, self_steps, opp_steps, res)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            self_steps = cheb(nx, ny, rx, ry)
            opp_steps = cheb(ox, oy, rx, ry)
            # lead positive means we get there earlier (or tie-break via steps)
            lead = opp_steps - self_steps
            # discourage equal-time races where opponent likely matches
            tie_pen = 0 if lead > 0 else (-2 if lead == 0 else 0)
            self_bias = -self_steps
            score = lead * 100 + tie_pen + self_bias
            cand = (score, self_steps, opp_steps, (rx, ry))
            if cand[0] > best_for_move[0] or (cand[0] == best_for_move[0] and (cand[1], cand[2]) < (best_for_move[1], best_for_move[2])):
                best_for_move = cand
        if best is None or (best_for_move[0], -best_for_move[1], best_for_move[3][0], best_for_move[3][1]) > (best[0], best[1], best[2], best[3]):
            best = (best_for_move[0], -best_for_move[1], best_for_move[3][0], best_for_move[3][1], dx, dy)

    return [best[4], best[5]]