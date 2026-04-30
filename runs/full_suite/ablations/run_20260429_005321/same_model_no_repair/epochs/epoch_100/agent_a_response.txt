def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    adj8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    def danger(x, y):
        if (x, y) in obst: 
            return 10**6
        d = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obst:
                d += 2
        return d

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        # pick target deterministically: nearest by Chebyshev, tie by x then y
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd or (d == bestd and (rx, ry) < best):
                bestd = d
                best = (rx, ry)
        tx, ty = best

        bestmove = (0, 0)
        bestscore = -10**18
        for dx, dy, nx, ny in legal:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # progress to resource dominates; secondarily slow opponent
            score = (-8 * ds) + (2 * do) - (1 * danger(nx, ny))
            # tiny deterministic bias to break ties toward moving "down-right"
            score += 0.001 * (nx + ny)
            if score > bestscore:
                bestscore = score
                bestmove = (dx, dy)
        return [int(bestmove[0]), int(bestmove[1])]

    # No resources: move toward opponent's direction while avoiding obstacles; also favor center
    cx, cy = (w - 1) / 2, (h - 1) / 2
    bestmove = (0, 0)
    bestscore = -10**18
    for dx, dy, nx, ny in legal:
        toward_op = -cheb(nx, ny, ox, oy)
        toward_center = -cheb(nx, ny, cx, cy)
        score = (2.5 * toward_op) + (0.8 * toward_center) - (1.2 * danger(nx, ny))
        score += 0.001 * (nx * 3 - ny * 2)  # deterministic tie-break
        if score > bestscore:
            bestscore = score
            bestmove = (dx, dy)
    return [int(bestmove[0]), int(bestmove[1])]