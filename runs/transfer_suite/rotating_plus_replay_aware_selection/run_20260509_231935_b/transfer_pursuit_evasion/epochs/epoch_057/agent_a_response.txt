def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    # If roles are unclear, default to pursuer behavior.
    i_am_pursuer = ("pursuer" in self_role) or (opp_role == "evader" and "pursuer" in self_role) or ("evader" not in self_role and "pursuer" not in opp_role)

    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx*dx + dy*dy

    def center_bias(x, y):
        return abs(x - cx) + abs(y - cy)

    # If evader, also bias toward staying in/near corners away from opponent.
    def corner_dist(x, y):
        corners = [(0,0), (0,h-1), (w-1,0), (w-1,h-1)]
        best = None
        for (tx, ty) in corners:
            d = (x-tx)*(x-tx) + (y-ty)*(y-ty)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d = dist2(nx, ny)
        # Deterministic composite score; pursuer minimizes distance, evader maximizes.
        if i_am_pursuer:
            # Prefer closer and also slightly toward center to avoid being cornered behind obstacles.
            score = (d, center_bias(nx, ny))
            key = score  # smaller is better
            if best_score is None or key < best_score:
                best_score = key
                best_move = [dx, dy]
        else:
            # Evader: maximize distance, prefer corners and avoid center.
            score = (d, -corner_dist(nx, ny), center_bias(nx, ny))
            # For evader: maximize d; minimize (-corner_dist) == maximize corner_dist; and minimize center_bias.
            key = (-score[0], score[1], score[2])  # convert to minimization
            if best_score is None or key < best_score:
                best_score = key
                best_move = [dx, dy]

    return best_move