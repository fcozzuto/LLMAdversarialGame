def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        dx = 0
        dy = 0
        best = -10**9
        for ddx, ddy in dirs:
            nx, ny = sx + ddx, sy + ddy
            if not valid(nx, ny):
                continue
            score = cheb(ox, oy, nx, ny)
            if score > best:
                best = score
                dx, dy = ddx, ddy
        return [int(dx), int(dy)]

    best_adj = None
    for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]:
        nx, ny = sx + ddx, sy + ddy
        if valid(nx, ny) and (nx, ny) in set(resources):
            best_adj = (ddx, ddy)
            break
    if best_adj is not None:
        return [int(best_adj[0]), int(best_adj[1])]

    opp = cheb(ox, oy, sx, sy)
    best_move = (0, 0)
    best_score = -10**18
    res_set = set(resources)

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        d_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        d_opp_to = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        gain = (d_opp_to - d_self)  # prefer positions that reduce our distance vs theirs
        steer = cheb(nx, ny, ox, oy) - opp  # also keep some space from opponent
        block = 1 if (nx, ny) not in res_set else -1
        score = -d_self * 10 + gain * 6 + steer * 2 - block
        if score > best_score:
            best_score = score
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]