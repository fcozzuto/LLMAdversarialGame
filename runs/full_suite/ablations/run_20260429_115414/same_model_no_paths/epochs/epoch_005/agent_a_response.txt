def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def obs_pen(x, y):
        if not obs:
            return 0
        best = 999
        for (px, py) in obs:
            d = cheb(x, y, px, py)
            if d < best: best = d
        return 0 if best >= 3 else (3 - best)
    def eval_pos(mx, my):
        # Advantage uses opponent distance minus my distance, both obstacle-aware.
        best_adv = -9999
        opp_closer_cnt = 0
        for (rx, ry) in resources:
            if (rx, ry) in obs:
                continue
            dm = cheb(mx, my, rx, ry) + obs_pen(mx, my) * 2
            do = cheb(ox, oy, rx, ry) + obs_pen(ox, oy) * 2
            adv = do - dm
            if adv > best_adv:
                best_adv = adv
            if do + 1 < dm:
                opp_closer_cnt += 1
        if best_adv == -9999:
            best_adv = -cheb(mx, my, w // 2, h // 2)
        # If opponent can get many resources sooner, heavily penalize.
        # Also keep some distance from opponent to reduce direct contest.
        dist_opp = cheb(mx, my, ox, oy)
        return best_adv - opp_closer_cnt * 2 - (7 - dist_opp if dist_opp < 7 else 0) * 0.5
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = eval_pos(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]