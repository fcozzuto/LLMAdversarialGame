def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = {(int(x), int(y)) for x, y in obstacles}
    res = [(int(x), int(y)) for x, y in resources]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_block(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obs: c += 1
        return c

    def best_target_score(nx, ny):
        if not res:
            return 0
        best = -10**18
        for rx, ry in res:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            gap_now = opp_d - our_d  # positive means we are sooner
            # also reward taking if we are effectively on top
            take = 1 if our_d == 0 else 0
            # contest pressure: prioritize resources where opponent is currently closer
            contest = 1 if opp_d <= 2 else 0
            v = 2.2 * gap_now + 3.0 * take + 0.9 * contest - 0.08 * our_d
            best = v if v > best else best
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Strongly avoid being adjacent to opponent unless it helps contest.
        prox = cheb(nx, ny, ox, oy)
        stay_clear = -1.4 if prox <= 1 else 0.0
        block_pen = -0.35 * near_block(nx, ny)
        val = best_target_score(nx, ny) + stay_clear + block_pen
        # tie-break toward reducing distance to opponent to enable interceptions, else toward nearer resource
        if val > best_val + 1e-9:
            best_val = val; best_move = [dx, dy]
        elif abs(val - best_val) <= 1e-9:
            if cheb(nx, ny, ox, oy) < cheb(sx + best_move[0], sy + best_move[1], ox, oy):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]