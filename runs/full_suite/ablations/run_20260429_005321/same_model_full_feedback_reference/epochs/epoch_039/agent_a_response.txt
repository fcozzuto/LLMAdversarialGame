def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        target = (tx, ty)
    else:
        best = None
        bestv = 10**18
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            v = md - 0.25 * od  # race for resources
            if v < bestv:
                bestv = v
                best = (rx, ry)
        target = best

    tx, ty = target
    bestm = (0, 0)
    bestscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        new_md = cheb(nx, ny, tx, ty)
        new_od = cheb(ox, oy, tx, ty)
        score = -new_md + 0.20 * new_od  # keep pressure on the race
        # encourage moving towards target when close
        score += 0.05 * cheb(nx, ny, ox, oy) * (-1 if resources else 1)
        if score > bestscore:
            bestscore = score
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]