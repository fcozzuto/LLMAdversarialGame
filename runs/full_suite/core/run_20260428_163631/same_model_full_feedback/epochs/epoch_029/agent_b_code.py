def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    if resources:
        def best_target(nx, ny):
            best_d = 10**9
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if d < best_d:
                    best_d = d
            return best_d
    else:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corners = [c for c in corners if ok(c[0], c[1])]
        if not corners:
            corners = [(0, 0)]
        def best_target(nx, ny):
            # use "farthest corner" via negative min-distance
            best_corner_dist = -10**9
            for cx, cy in corners:
                d = dist(nx, ny, cx, cy)
                if d > best_corner_dist:
                    best_corner_dist = d
            return -best_corner_dist  # lower is better overall in scoring

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        t = best_target(nx, ny)
        # If resources exist: t is min distance -> smaller is better.
        # If no resources: t is negative "corner dist" -> smaller is better, so effectively maximize corner dist.
        opp_d = dist(nx, ny, ox, oy)
        score = -t * 100 - opp_d
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]