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
    pursuer = (not self_ev) or opp_ev

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (0, 0)
    best_score = None
    dist0 = cheb(sx, sy, ox, oy)

    if pursuer:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            # prefer bigger reduction; tie-break with closeness to center
            score = (dist0 - d, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2))
            if best_score is None or score > best_score:
                best_score, best = score, (dx, dy)
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # target farthest corner from pursuer to counter "evasion_corner"
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d_op = cheb(nx, ny, ox, oy)
            d_tc = cheb(nx, ny, tx, ty)
            # maximize distance from pursuer; also keep heading to target corner
            score = (d_op, -d_tc)
            if best_score is None or score > best_score:
                best_score, best = score, (dx, dy)

    return [int(best[0]), int(best[1])]