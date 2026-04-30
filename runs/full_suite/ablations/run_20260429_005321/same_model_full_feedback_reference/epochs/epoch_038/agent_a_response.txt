def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # drift target when no resources
    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        d0x = 1 if sx < tx else (-1 if sx > tx else 0)
        d0y = 1 if sy < ty else (-1 if sy > ty else 0)
        for dx, dy in [(d0x, d0y),(d0x,0),(0,d0y),(0,0)]:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny): 
                return [dx, dy]
        return [0, 0]

    # Prefer moves that reduce our distance to a resource while keeping opponent farther.
    best = None
    bestv = -10**18
    opp_cur_d = cheb(ox, oy, sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        my_min = 10**9
        opp_best_pen = -10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # main: move toward resources; secondary: choose where we are ahead of opponent
            my_min = d_my if d_my < my_min else my_min
            opp_best_pen = max(opp_best_pen, d_op - d_my)

        # tie-breakers: avoid being too close to opponent early; also avoid stepping into "contested" clusters
        val = (opp_best_pen * 50) - (my_min * 8)
        val += 3 if cheb(nx, ny, ox, oy) > opp_cur_d else -1
        # deterministic small bias by coordinates to break ties consistently
        val += (nx * 3 + ny) * 0.001

        if val > bestv:
            bestv = val
            best = (dx, dy)

    return [best[0], best[1]]