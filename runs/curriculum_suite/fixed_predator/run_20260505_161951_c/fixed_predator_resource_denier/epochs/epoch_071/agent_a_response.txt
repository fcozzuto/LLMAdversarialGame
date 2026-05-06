def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(px, py):
        return 0 <= px < w and 0 <= py < h and (px, py) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def opp_best_step(tx, ty):
        best = (10**9, (0, 0))
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, (dx, dy))
        return best[0]

    if not resources:
        tx, ty = w - 1, h - 1
        bestm = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = (cheb(nx, ny, ox, oy) * 50) - (abs(nx - tx) + abs(ny - ty))
            if v > bestv:
                bestv = v; bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    bestm = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        my_d = 10**9
        best_resource_score = -10**18
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            if d_my < my_d:
                my_d = d_my
            d_opp = opp_best_step(rx, ry)
            # Prefer making it harder for opponent while keeping good pickup distance for us.
            rem = 1.0
            # If move lands on resource, strongly commit.
            if nx == rx and ny == ry:
                s = 10**7
            else:
                s = (d_opp - d_my) * 120 - d_my * 8 - rem
            if s > best_resource_score:
                best_resource_score = s
        # Also avoid stepping toward opponent too aggressively unless winning.
        risk = cheb(nx, ny, ox, oy)
        v = best_resource_score + risk * 2
        if v > bestv:
            bestv = v; bestm = (dx, dy)
    return [bestm[0], bestm[1]]