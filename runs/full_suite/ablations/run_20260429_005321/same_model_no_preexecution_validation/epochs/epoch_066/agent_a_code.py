def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}
    res = [(int(p[0]), int(p[1])) for p in resources]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obs: c += 1
        return c

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    best = None
    best_score = -10**18

    if res:
        # Prefer: get closer to nearest resource, avoid opponent, avoid obstacles.
        for dx, dy, nx, ny in cand:
            dmin = 10**9
            for rx, ry in res:
                d = cheb(nx, ny, rx, ry)
                if d < dmin: dmin = d
            opp = cheb(nx, ny, ox, oy)
            # Make capturing/contesting resources attractive and deterministic.
            # Base: minimize distance to resources => larger score.
            score = -dmin
            score += 0.05 * opp
            score -= 0.3 * near_obs(nx, ny)
            # If in same cell as a resource (possible if resources persist), boost strongly.
            if (nx, ny) in obs:
                score -= 1000
            if (nx, ny) in set(res):
                score += 50
            # Encourage keeping direction toward resources deterministically.
            score += -0.01 * cheb(nx, ny, sx, sy)
            if score > best_score:
                best_score = score; best = (dx, dy)
    else:
        # No resources: head to the corner farthest from opponent, avoid obstacles.
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        target = None; bestfar = -1
        for cx, cy in corners:
            if (cx, cy) in obs: 
                continue
            d = cheb(cx, cy, ox, oy)
            if d > bestfar:
                bestfar = d; target = (cx, cy)
        if target is None:
            target = (0, 0)
        tx, ty = target
        for dx, dy, nx, ny in cand:
            score = cheb(nx, ny, ox, oy)  # maximize distance from opponent
            score += 0.5 * cheb(tx, ty, nx, ny) * -1  # move toward chosen corner
            score -= 0.3 * near_obs(nx, ny)
            if score > best_score:
                best_score = score; best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]