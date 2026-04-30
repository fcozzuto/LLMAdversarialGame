def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obst = set((p[0], p[1]) for p in obstacles)
    res = [(p[0], p[1]) for p in resources]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def near_pen(x, y):
        p = 0
        if (x, y) in obst:
            return 10**9
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            if (x+dx, y+dy) in obst:
                p += 1
        return p

    best = (-10**18, (0, 0))
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pen = near_pen(nx, ny)
        if pen >= 10**8:
            continue
        if not res:
            score = -pen
        else:
            best_t = -10**18
            for rx, ry in res:
                dm = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # prefer moves that are ahead (smaller dm than do), then closer resource
                t = (do - dm) * 100 - dm - pen * 5
                if t > best_t:
                    best_t = t
            score = best_t
        if score > best[0]:
            best = (score, (dx, dy))
        elif score == best[0]:
            # deterministic tie-break: prefer staying or smaller step
            cd = abs(dx) + abs(dy)
            bd = abs(best[1][0]) + abs(best[1][1])
            if cd < bd or (cd == bd and (dx, dy) < best[1]):
                best = (score, (dx, dy))
    return [best[1][0], best[1][1]]