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
    i_am_pursuer = ("pursuer" in self_role) or ("evader" not in self_role and "pursuer" not in opp_role)

    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx*dx + dy*dy

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    def center_bias(x, y):
        return abs(x - cx) + abs(y - cy)

    corners = [(0,0), (0,h-1), (w-1,0), (w-1,h-1)]
    def corner_far(x, y):
        best = 0
        for cx0, cy0 in corners:
            d = abs(x - cx0) + abs(y - cy0)
            if d > best:
                best = d
        return best

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist2(nx, ny)
        if i_am_pursuer:
            # chase while preferring moves that keep central pressure (avoid cornering too early)
            score = d + 0.05 * center_bias(nx, ny)
        else:
            # evade: maximize distance, then increase corner-ness away from opponent
            score = -d + 0.02 * center_bias(nx, ny) - 0.01 * corner_far(nx, ny)
        key = (score, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1] if best is not None else [0, 0]