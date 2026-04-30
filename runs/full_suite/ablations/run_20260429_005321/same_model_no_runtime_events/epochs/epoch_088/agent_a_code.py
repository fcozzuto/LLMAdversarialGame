def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # Go toward opponent's side while avoiding obstacles locally
        best = [0, 0]
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, w - 1, h - 1) if (sx + sy) < (w-1 + h-1) else cheb(nx, ny, 0, 0)
            v = -v
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick target deterministically: prefer resources where we are not behind opponent
    my_best = None
    for rx, ry in resources:
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we are closer or tied, strongly prefer; otherwise penalize.
        score = (do - dm) * 100 - dm
        if my_best is None or score > my_best[0]:
            my_best = [score, rx, ry]
    target_x, target_y = my_best[1], my_best[2]

    # Local greedy move with obstacle-aware tie-breaking and mild opponent avoidance
    best = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dm_next = cheb(nx, ny, target_x, target_y)
        dm_now = cheb(sx, sy, target_x, target_y)
        # Encourage progress; discourage stepping closer to opponent too much.
        opp_closer = (cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy))
        step_gain = (dm_now - dm_next)
        s = step_gain * 1000 - dm_next
        if opp_closer:
            s -= 20
        # Small deterministic bias to spread diagonally when equal
        if dx != 0 and dy != 0:
            s += 1
        if s > best_score:
            best_score = s
            best = [dx, dy]

    return best