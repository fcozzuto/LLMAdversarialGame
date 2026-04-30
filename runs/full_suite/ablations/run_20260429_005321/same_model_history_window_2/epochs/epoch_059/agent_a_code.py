def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def min_dist_to_resources(x, y):
        if not resources:
            return 10**9
        m = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < m:
                m = d
        return m

    curr_to_res = min_dist_to_resources(sx, sy)
    curr_to_opp = cheb(sx, sy, ox, oy)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dres = min_dist_to_resources(nx, ny)
        dopp = cheb(nx, ny, ox, oy)
        gain = curr_to_res - dres
        block = dres - min_dist_to_resources(ox, oy)
        score = gain * 10 + block * 2 + (dopp - curr_to_opp) * 0.5
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                best = (dx, dy)
                break
    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]