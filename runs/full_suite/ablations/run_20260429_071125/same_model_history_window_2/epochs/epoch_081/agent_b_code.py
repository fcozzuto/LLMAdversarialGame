def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_score = -10**18

    next_is_resource = set(res)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obst:
            continue

        score = 0
        if (nx, ny) in next_is_resource:
            score += 10000

        if res:
            dmin = min(cheb(nx, ny, rx, ry) for rx, ry in res)
            score += (50 - dmin * 5)

        if (ox, oy) != (sx, sy):
            dop = cheb(nx, ny, ox, oy)
            if dop <= 1:
                score -= 300
            elif dop == 2:
                score -= 100
            elif dop <= 4:
                score -= 25

        if obst:
            db = min(cheb(nx, ny, ax, ay) for ax, ay in obst)
            if db == 0:
                score -= 100000
            elif db == 1:
                score -= 50
            elif db == 2:
                score -= 20

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move