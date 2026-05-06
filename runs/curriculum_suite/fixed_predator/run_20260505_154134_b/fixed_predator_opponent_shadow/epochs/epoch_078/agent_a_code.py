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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    # Evaluate each move by choosing the best resource for the resulting position.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_res = None
        best_res_key = None
        for cx, cy in resources:
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # Prefer grabbing resources where we become closer than opponent; otherwise prefer reducing their lead.
            key = (opp_d - self_d, -self_d, -cx, -cy)
            if best_res_key is None or key > best_res_key:
                best_res_key = key
                best_res = (cx, cy)

        # Tie-break: also prefer moves that reduce our distance to the best target and avoid getting too close to opponent.
        cx, cy = best_res
        self_d = cheb(nx, ny, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        opp_prox = cheb(nx, ny, ox, oy)  # higher is safer
        val = (opp_d - self_d) * 1000 + (opp_prox) * 2 - self_d
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best