def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)

    # If there is a resource, move toward closest resource with a bias to stay away from opponent
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d_me = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # score favors closer to resource and being farther from opponent
            score = -d_me + (d_opp * -0.5)
            if best is None or score > best_score:
                best = (rx, ry)
                best_score = score
        if best:
            tx, ty = best
            # choose step toward target
            dx = 0
            dy = 0
            if tx > sx: dx = 1
            elif tx < sx: dx = -1
            if ty > sy: dy = 1
            elif ty < sy: dy = -1
            nb = (sx + dx, sy + dy)
            if legal(nb[0], nb[1]):
                return [dx, dy]
            # if blocked, try any legal step toward target with fallback
            for dx2, dy2 in dirs:
                nx, ny = sx + dx2, sy + dy2
                if (dx2, dy2) != (0, 0) and legal(nx, ny):
                    return [dx2, dy2]
            return [0, 0]

    # No resources or couldn't reach one: move to maximize distance from opponent while staying safe
    best = None
    best_score = None
    for dx, dy in dirs:
        if dx == 0 and dy == 0:
            continue
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_opp = dist((nx, ny), (ox, oy))
        d_me = dist((nx, ny), (nx, ny))  # always 0; placeholder to keep deterministic structure
        # simpler: maximize distance to opponent
        score = d_opp
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is not None:
        return [best[0], best[1]]

    # stay if no move found
    return [0, 0]