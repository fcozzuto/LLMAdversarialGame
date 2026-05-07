def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    res_set = set(resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Gain: how much closer we are than opponent to the same resource
        if (nx, ny) in res_set:
            val = 10**9 + cheb(nx, ny, ox, oy)  # prefer immediate collection, then keep distance
        else:
            best_own_disadv = -10**18
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # maximize (opponent distance - self distance) to secure targets
                own_disadv = od - sd
                if own_disadv > best_own_disadv:
                    best_own_disadv = own_disadv
            # slight secondary preference: move that most reduces our distance to the closest resource
            closest_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            val = best_own_disadv * 1000 - closest_self

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]