def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obst.add((px, py))
        except:
            pass

    res_list = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obst:
                res_list.append((rx, ry))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None
    best_score = None

    if res_list:
        # Pursue nearest resource not blocked
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dbest = None
            for rx, ry in res_list:
                d = cheb((nx, ny), (rx, ry))
                if dbest is None or d < dbest:
                    dbest = d
            score = - (dbest if dbest is not None else 0)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
    else:
        # If no resources visible, approach closer to opponent to contest center
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb((nx, ny), (ox, oy))
            score = -d
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]