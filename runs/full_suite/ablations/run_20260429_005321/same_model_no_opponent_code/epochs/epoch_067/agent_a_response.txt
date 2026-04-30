def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def to_xy(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (int(p[0]), int(p[1]))
        return None

    obstacles = set()
    for p in observation.get("obstacles") or []:
        q = to_xy(p)
        if q is not None:
            obstacles.add(q)

    resources = []
    for p in observation.get("resources") or []:
        q = to_xy(p)
        if q is not None and q not in obstacles:
            resources.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def min_dist_to_resources(x, y):
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return cheb(x, y, int(cx), int(cy))
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    def min_dist_to_opponent(x, y):
        return cheb(x, y, ox, oy)

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dres = min_dist_to_resources(nx, ny)
        dop = min_dist_to_opponent(nx, ny)

        cell_score = (dop, -dres)  # farther from opponent, closer to resources
        if best_score is None or cell_score > best_score:
            best_score = cell_score
            best_move = [dx, dy]

    return best_move