def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        dx = 0 if sx == 0 else (-1 if sx > w - 1 - sx else 1)
        dy = 0 if sy == 0 else (-1 if sy > h - 1 - sy else 1)
        best = None
        bestv = 10**9
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if not inb(nx, ny): 
                continue
            v = cheb(nx, ny, w - 1 - ox, h - 1 - oy)
            if v < bestv:
                bestv = v
                best = [ddx, ddy]
        return best if best is not None else [0, 0]

    best_move = [0, 0]
    best_val = 10**9

    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny):
            continue

        # Relative advantage: smaller is better (we aim to be closer than opponent)
        # Primary: minimize (my_dist - opp_dist). Secondary: minimize my_dist.
        local_best = 10**9
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            rel = md - od
            # Prefer taking a resource where we are not losing, and get it sooner.
            val = (rel * 10) + md
            if val < local_best:
                local_best = val

        # Also avoid drifting into being adjacent to opponent too early if equally good
        opp_close = 0 if cheb(nx, ny, ox, oy) > 1 else 1
        local_best = local_best + opp_close * 2

        if local_best < best_val:
            best_val = local_best
            best_move = [ddx, ddy]

    return [int(best_move[0]), int(best_move[1])]