def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        bestd = 10**9
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if d < bestd:
                bestd = d
                target = (x, y)

    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if target is not None:
            d = cheb(nx, ny, target[0], target[1])
            opp = cheb(nx, ny, ox, oy)
            score = (0 if d == 0 else d) * 100 - opp
        else:
            opp = cheb(nx, ny, ox, oy)
            score = -opp
        scored.append((score, dx, dy))

    if not scored:
        return [0, 0]
    scored.sort()
    return [scored[0][1], scored[0][2]]