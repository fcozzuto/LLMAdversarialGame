def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    def to_xy(p):
        if p is None:
            return None
        if isinstance(p, dict):
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
            if 0 in p and 1 in p:
                return int(p[0]), int(p[1])
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        return None
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    sp = to_xy(observation.get("self_position"))
    op = to_xy(observation.get("opponent_position"))
    if sp is None:
        return [0, 0]
    sx, sy = sp
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        t = to_xy(p)
        if t is not None:
            obs.add(t)
    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        t = to_xy(p)
        if t is not None:
            targets.append(t)
    unclaimed = observation.get("unclaimed_cells") or []
    un = []
    for p in unclaimed:
        t = to_xy(p)
        if t is not None:
            un.append(t)
    opp_penalty = 0
    if op is not None:
        ox, oy = op
        opp_penalty = 10
    else:
        ox, oy = sx, sy

    moves = [(-1,0),(1,0),(0,-1),(0,1),(0,0)]
    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if targets:
            md = min(abs(nx-tx)+abs(ny-ty) for tx, ty in targets)
            score += -2*md
        elif un:
            md = min(abs(nx-tx)+abs(ny-ty) for tx, ty in un)
            score += -md
        else:
            score += -abs(nx-ox)-abs(ny-oy)
        if op is not None:
            dist_opp = abs(nx-ox)+abs(ny-oy)
            score += opp_penalty * (dist_opp <= 1) - dist_opp
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]