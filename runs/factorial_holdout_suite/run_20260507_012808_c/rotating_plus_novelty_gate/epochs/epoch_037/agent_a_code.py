def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    if sx < 0: sx = 0
    if sy < 0: sy = 0
    if sx >= w: sx = w - 1
    if sy >= h: sy = h - 1
    if ox < 0: ox = 0
    if oy < 0: oy = 0
    if ox >= w: ox = w - 1
    if oy >= h: oy = h - 1

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    onres = set()
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                onres.add((x, y))
        except:
            pass

    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    def cheb(ax, ay, bx, by):
        ax -= bx
        if ax < 0: ax = -ax
        ay -= by
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    best = None
    best_score = -10**18
    any_valid = False

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        any_valid = True
        if (nx, ny) in onres:
            score = 100000
            best_move = [dx, dy]
            if score > best_score:
                best_score = score
                best = best_move
            continue
        mind_res = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < mind_res:
                mind_res = d
        mind_opp = cheb(nx, ny, ox, oy)
        score = -mind_res * 10 + mind_opp
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    if any_valid:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
    return [0, 0]