def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)
    chase = (not self_ev) or opp_ev

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist(x, y, tx, ty):
        dx = x - tx
        if dx < 0: dx = -dx
        dy = y - ty
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for d in dirs:
        nx, ny = sx + d[0], sy + d[1]
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        ad = dist(nx, ny, ox, oy)
        score = ad if chase else -ad
        if best_score is None or score > best_score:
            best_score = score
            best = [int(d[0]), int(d[1])]
    if best is not None:
        return best

    for d in dirs:
        nx, ny = sx + d[0], sy + d[1]
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(d[0]), int(d[1])]
    return [0, 0]