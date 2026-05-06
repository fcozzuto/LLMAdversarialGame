def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(obstacles)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        bestv = 10**9
        cx = w // 2
        cy = h // 2
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            v = d * 1000 + abs(rx - cx) + abs(ry - cy)
            if v < bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best
        threatx, threaty = ox, oy
    else:
        tx, ty = (0, h - 1) if x < w // 2 else (w - 1, 0)
        threatx, threaty = ox, oy

    bestmove = (0, 0)
    bestscore = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        # Prefer reducing distance to target, avoid moving toward opponent if no resources
        dtar = cheb(nx, ny, tx, ty)
        score = -dtar * 1000
        if resources:
            # small nudge to discourage getting too close to opponent
            score -= cheb(nx, ny, ox, oy) * 5
        else:
            # with no resources, keep away from opponent
            score += cheb(nx, ny, threatx, threaty) * 10
        # deterministic tie-break: prefer smaller (dx,dy) lexicographically
        if score > bestscore or (score == bestscore and (dx, dy) < bestmove):
            bestscore = score
            bestmove = (dx, dy)

    return [bestmove[0], bestmove[1]]