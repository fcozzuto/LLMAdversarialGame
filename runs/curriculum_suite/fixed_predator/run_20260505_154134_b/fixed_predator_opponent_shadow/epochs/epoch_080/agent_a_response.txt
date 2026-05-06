def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    if not resources:
        return [0, 0]

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

    # Choose best target: (opponent advantage, then closer to us, then deterministic tie-break)
    best_t = None
    best_k = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        k = (opp_d - self_d, -self_d, -cx, -cy)
        if best_k is None or k > best_k:
            best_k, best_t = k, (cx, cy)
    tx, ty = best_t

    # If we can take a resource immediately, do it (prioritizing where we beat opponent)
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    res_set = set((int(r[0]), int(r[1])) for r in resources)
    immediate = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in res_set:
            self_d = 0
            opp_d = cheb(ox, oy, nx, ny)
            k = (opp_d - self_d, -self_d, -nx, -ny)
            immediate.append((k, dx, dy))
    if immediate:
        immediate.sort(key=lambda t: t[0], reverse=True)
        return [immediate[0][1], immediate[0][2]]

    # Otherwise, move to improve relative progress toward target and deny opponent
    best = None
    best_k = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # target progress
        self_to_t = cheb(nx, ny, tx, ty)
        self_cur_t = cheb(sx, sy, tx, ty)
        # opponent threat: being closer to opponent than us near the target is bad
        opp_to_t = cheb(ox, oy, tx, ty)
        # prefer reducing our distance, and making opponent relatively farther from target
        rel = (opp_to_t - cheb(ox, oy, nx, ny))  # larger => opponent less aligned with next pos
        k = (-(self_to_t - self_cur_t), self_to_t, -rel, -nx, -ny)
        if best_k is None or k > best_k:
            best_k, best = k, (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]