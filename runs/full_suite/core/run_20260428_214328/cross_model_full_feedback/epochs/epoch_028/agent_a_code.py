def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obst.add((int(p[0]), int(p[1])))
        except:
            pass
    resources = []
    for p in (observation.get("resources", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            resources.append((x, y))
        except:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target = None
    if resources:
        bx, by = resources[0]
        best = cheb(sx, sy, bx, by)
        for (rx, ry) in resources[1:]:
            d = cheb(sx, sy, rx, ry)
            if d < best:
                best = d
                bx, by = rx, ry
        target = (bx, by)

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if target is None:
            dist_to_target = cheb(nx, ny, ox, oy)
        else:
            dist_to_target = cheb(nx, ny, target[0], target[1])
        dist_from_opp = cheb(nx, ny, ox, oy)
        score = -dist_to_target + 0.01 * dist_from_opp
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move