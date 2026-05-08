def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = r
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
        except:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def near_obst(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    p += 1
        return p

    before = cheb(sx, sy, ox, oy)
    if res:
        best = None
        bestv = -10**9
        for tx, ty in res:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            v = (do - ds) * 10 - ds
            if v > bestv:
                bestv = v
                best = (tx, ty)
        tx, ty = best
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = -10**18
    dtarget_before = cheb(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        adt = cheb(nx, ny, tx, ty)
        dp = cheb(nx, ny, ox, oy)
        dtarget_improve = dtarget_before - adt
        dpo = dp - before
        avoid = 0
        if dp <= 2:
            avoid = (2 - dp) * 4
        score = dtarget_improve * 10 + dpo * 2 - near_obst(nx, ny) * 6 - avoid
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]