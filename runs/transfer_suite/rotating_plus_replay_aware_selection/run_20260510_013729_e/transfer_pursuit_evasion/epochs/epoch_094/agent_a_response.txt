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
    evading = self_ev or ((not opp_ev) and self_role == "" and ("evad" not in self_role and "purs" not in self_role))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    fcx, fcy = far_corner

    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_op = cheb(nx, ny, ox, oy)

        if evading:
            # Prefer maximizing distance; also bias toward farthest corner.
            # Secondary: avoid proximity to obstacles.
            obst_min = 10
            for (bx, by) in obs:
                dd = cheb(nx, ny, bx, by)
                if dd < obst_min: obst_min = dd
            score = (d_to_op * 100) + (cheb(nx, ny, fcx, fcy) * 3) + obst_min
            better = (best_score is None) or (score > best_score)
        else:
            # Pursue: minimize distance; try to block by aiming one step beyond opponent direction away from us.
            # Approximate "away direction" from our position.
            ax = 0 if ox == sx else (1 if ox > sx else -1)
            ay = 0 if oy == sy else (1 if oy > sy else -1)
            tx, ty = ox + ax, oy + ay
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
                tx, ty = ox, oy
            d_to_target = cheb(nx, ny, tx, ty)
            obst_pen = 0
            for (bx, by) in obs:
                if cheb(nx, ny, bx, by) <= 1:
                    obst_pen += 2
            score = (-d_to_target * 100) + (-d_to_op * 20) - obst_pen
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_move = [dx, dy]

    return best_move