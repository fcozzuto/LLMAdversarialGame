def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # If there are resources, move toward nearest resource, prioritizing gaining on distance to resource relative to opponent
    if resources:
        best_move = None
        best_score = None
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_bounds(nx, ny):
                continue
            # distance to closest resource after move
            dme = min(cheb((nx, ny), r) for r in resources)
            # opponent distance to closest resource
            dop = min(cheb((ox, oy), r) for r in resources)
            # score: prefer reducing own distance to resource and increasing distance from opponent to resource
            score = (dme, -dop)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        if best_move is not None:
            return [best_move[0], best_move[1]]

    # Otherwise, go toward center while avoiding obstacles and staying ahead of opponent if possible
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = None
    best_metric = None
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny):
            continue
        # metric: proximity to center minus opponent proximity to center
        dme = cheb((nx, ny), (cx, cy))
        dop = cheb((ox, oy), (cx, cy))
        metric = (dme, dop)
        if best_metric is None or metric < best_metric:
            best_metric = metric
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    # Fallback: stay
    return [0, 0]