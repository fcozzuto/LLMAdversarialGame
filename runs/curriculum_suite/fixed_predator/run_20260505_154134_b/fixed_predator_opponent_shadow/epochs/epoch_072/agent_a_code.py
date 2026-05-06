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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # For this candidate, pick our best resource while accounting for opponent pressure.
        cand_best = None
        cand_key = None
        for cx, cy in resources:
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # Prefer resources opponent is closer to (we can steal), then nearest overall.
            key = (opp_d - self_d, -self_d, -cx, -cy)
            if cand_key is None or key > cand_key:
                cand_key = key
                cand_best = (cx, cy)

        # If no valid resource (shouldn't happen), fall back to nearest move.
        if cand_key is None:
            key2 = (-10**9,)
        else:
            cx, cy = cand_best
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # Add small tie-break: prefer moving away from opponent when equally pressured.
            key2 = (cand_key[0], cand_key[1], opp_d == self_d, -cheb(nx, ny, ox, oy), cand_key[2], cand_key[3])

        if best_key is None or key2 > best_key:
            best_key = key2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]