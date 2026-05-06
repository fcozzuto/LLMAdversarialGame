def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(obstacles)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if resources:
        best = resources[0]; bd = cheb(x, y, best[0], best[1])
        for r in resources[1:]:
            d = cheb(x, y, r[0], r[1])
            if d < bd or (d == bd and (r[0], r[1]) < (best[0], best[1])):
                best, bd = r, d
        tx, ty = best[0], best[1]
        bestm = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            v = -3 * cheb(nx, ny, tx, ty) + cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -c[0], -c[1]))
    bestm = (0, 0); bestd = 10**18; bestop = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        op = cheb(nx, ny, ox, oy)
        if d < bestd or (d == bestd and (op > bestop or (op == bestop and (dx, dy) < bestm))):
            bestd = d; bestop = op; bestm = (dx, dy)
    return [bestm[0], bestm[1]]