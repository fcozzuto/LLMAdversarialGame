def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    def as_xy(p):
        if isinstance(p, dict):
            if "position" in p:
                p = p["position"]
            return int(p.get("x", p.get(0, 0))), int(p.get("y", p.get(1, 0)))
        return int(p[0]), int(p[1])
    sx, sy = as_xy([sx, sy]), as_xy([ox, oy]) if False else (int(sx), int(sy))
    ox, oy = int(ox), int(oy)
    sx, sy = int(sx), int(sy)

    obs_set = set()
    for p in obstacles:
        x, y = as_xy(p)
        obs_set.add((x, y))

    if not resources:
        return [0, 0]

    res_xy = []
    for r in resources:
        x, y = as_xy(r)
        if 0 <= x < w and 0 <= y < h:
            res_xy.append((x, y))
    if not res_xy:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def nearest_dist(x, y):
        md = 10**9
        for rx, ry in res_xy:
            d = man(x, y, rx, ry)
            if d < md: md = d
        return md

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best = None

    opp_next = (ox, oy)  # opponent assumed unchanged; scoring uses our move only
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obs_set:
            continue
        myd = nearest_dist(nx, ny)
        opd = nearest_dist(ox, oy)
        # Lead positive is better (we want smaller distance than opponent)
        lead = opd - myd
        score = (lead, -myd, -opd, dx, dy)
        if best is None or score > best:
            best = score
            best_move = [dx, dy]
    return best_move