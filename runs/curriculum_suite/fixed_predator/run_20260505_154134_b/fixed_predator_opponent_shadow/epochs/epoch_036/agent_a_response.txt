def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_adv(px, py):
        if not resources:
            return (-10**9, 0, (px, py))
        best = None
        for cx, cy in resources:
            self_d = cheb(px, py, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            adv = opp_d - self_d
            key = (adv, -self_d, cx, cy)
            if best is None or key > best[0]:
                best = (key, self_d)
        return (best[0][0], best[0][1], (best[0][2], best[0][3]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curr_adv, curr_neg_selfd, _ = best_adv(sx, sy)

    best_move = (0, 0)
    best_val = (-10**9, 10**9, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        adv, neg_selfd, _ = best_adv(nx, ny)
        # Prefer improving advantage; if tie, prefer staying closer; small penalty for moving away from current best
        val = (adv, neg_selfd, -cheb(nx, ny, sx, sy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If no improving moves found, commit to the best immediate direction toward the target of current state
    if best_val[0] < curr_adv:
        # deterministic: pick the resource with max adv, then move one step toward it (avoid obstacles)
        target = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(sx, sy, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            key = (opp_d - self_d, -self_d, cx, cy)
            if best_key is None or key > best_key:
                best_key = key
                target = (cx, cy)
        if target is None:
            return [0, 0]
        tx, ty = target
        stepx = 0 if tx == sx else (1 if tx > sx else -1)
        stepy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = [(stepx, stepy), (stepx, 0), (0, stepy), (0, 0), (-stepx, -stepy)]
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs and dx in (-1, 0, 1) and dy in (-1, 0, 1):
                return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]