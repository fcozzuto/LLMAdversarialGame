def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        if p is None:
            continue
        x, y = p
        obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("catch" in role) or ("purs" in opp_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p is None:
            continue
        x, y = p
        if inb(x, y):
            res.append((x, y))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1),(0,0)]
    best = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        if res:
            d_res = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        else:
            d_res = 0
        # Primary: approach if pursuer, evade otherwise. Secondary: move toward resources.
        primary = -d_opp if is_pursuer else d_opp
        key = (primary, -d_res, nx, ny, dx, dy)  # deterministic tiebreaks
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]