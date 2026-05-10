def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)
    act_as_evader = self_ev or (not opp_ev and "evad" not in self_role and "run" not in self_role and "escap" not in self_role and self_role == "")

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        if act_as_evader:
            # maximize distance to opponent, then maximize distance to nearest corner (stick to safe corner if possible)
            d_opp = cheb(nx, ny, ox, oy)
            d_corner = min(cheb(nx, ny, cx, cy) for cx, cy in corners)
            score = (d_opp, d_corner)
        else:
            # minimize distance to opponent, tie-break by moving toward the farthest corner (avoid getting trapped near obstacles)
            d_opp = cheb(nx, ny, ox, oy)
            d_corner_far = min(cheb(nx, ny, cx, cy) for cx, cy in corners)
            score = (-d_opp, d_corner_far)

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move