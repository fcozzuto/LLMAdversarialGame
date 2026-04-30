def choose_move(observation):
    def pxy(v, d=0):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return d, d

    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = pxy(observation.get("self_position", [0, 0]))
    ox, oy = pxy(observation.get("opponent_position", [w - 1, h - 1]))

    obstacles = set()
    for q in observation.get("obstacles") or []:
        x, y = pxy(q)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for q in observation.get("resources") or []:
        x, y = pxy(q)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        cx = sum(x for x, _ in resources) / len(resources)
        cy = sum(y for _, y in resources) / len(resources)
        tx, ty = int(cx), int(cy)
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        else:
            dres = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)
        # Higher is better: get closer to resources and slightly away from opponent
        score = (-dres) + (0.15 * dop)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]