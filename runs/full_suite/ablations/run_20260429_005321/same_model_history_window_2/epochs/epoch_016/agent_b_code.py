def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obst.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
            resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    bestd = None
    for x, y in resources:
        d = cheb(sx, sy, x, y)
        if bestd is None or d < bestd or (d == bestd and (x + y, x, y) < (target[0] + target[1], target[0], target[1])):
            bestd = d
            target = (x, y)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        if target is not None:
            dist_t = cheb(nx, ny, target[0], target[1])
        else:
            dist_t = 0
        dist_o = cheb(nx, ny, ox, oy)
        move_score = 0
        if target is not None:
            move_score += (1000 - dist_t * 20)
            if resources and (nx, ny) == target:
                move_score += 100000
        move_score += dist_o * 5
        if (nx, ny) == (sx, sy) and target is None:
            move_score -= 1
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    nx, ny = sx + best_move[0], sy + best_move[1]
    if not inb(nx, ny) or (nx, ny) in obst:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]