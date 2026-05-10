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

    act_as_evader = self_ev or (self_role == "" and not opp_ev)
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

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_score = None

    # Slight obstacle-aware tie-break: prefer staying mobile (more free neighboring cells)
    def mobility(nx, ny):
        m = 0
        for dx, dy in dirs:
            x, y = nx + dx, ny + dy
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                m += 1
        return m

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            score = -10**9 if act_as_evader else 10**9
        else:
            d = cheb(nx, ny, ox, oy)
            if act_as_evader:
                # maximize distance; also prefer higher mobility
                score = d * 1000 + mobility(nx, ny)
            else:
                # minimize distance; also prefer higher mobility when distances tie
                score = -d * 1000 + mobility(nx, ny)
        if best is None or (act_as_evader and score > best_score) or ((not act_as_evader) and score > best_score):
            best = (dx, dy)
            best_score = score

    return [best[0], best[1]]