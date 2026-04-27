def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(obstacles)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mdist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx + dy

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def best_target():
        if not resources:
            return None
        best = None
        best_adv = -10**9
        my = (sx, sy)
        opp = (ox, oy)
        for r in resources:
            adv = mdist(opp, r) - mdist(my, r)
            if adv > best_adv:
                best_adv = adv
                best = r
        return best

    target = best_target()
    if target is None:
        # No resources: maximize distance from opponent (still legal)
        best = None
        best_score = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = mdist((nx, ny), (ox, oy))
            if score > best_score:
                best_score = score
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    my0 = (sx, sy)
    opp0 = (ox, oy)
    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds = mdist((nx, ny), target)
        do = mdist(opp0, target)
        score = (do - ds)
        # small deterministic bias toward progress
        score -= abs(nx - target[0]) + abs(ny - target[1]) * 0.001
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]