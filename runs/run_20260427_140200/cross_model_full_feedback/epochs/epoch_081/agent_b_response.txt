def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
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

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # If there are resources, move to the nearest in a tie-breaking by staying closer to objective of winning distance to resource minus opponent distance
    if resources:
        best = None
        best_score = 10**9
        for rx, ry in resources:
            dme = cheb((mx, my), (rx, ry))
            dop = cheb((ox, oy), (rx, ry))
            score = dme - dop  # prefer resources closer to me and farther from opponent
            if score < best_score:
                best_score = score
                best = (rx, ry)
        if best is not None:
            # choose a move that reduces distance to best resource while avoiding obstacles
            tx, ty = best
            best_move = None
            best_dist = 10**9
            for dx, dy in moves:
                nx, ny = mx + dx, my + dy
                if not in_bounds(nx, ny):
                    continue
                d = cheb((nx, ny), (tx, ty))
                if d < best_dist:
                    best_dist = d
                    best_move = (dx, dy)
            if best_move is not None:
                return [best_move[0], best_move[1]]

    # No resources or no suitable move toward resource; move toward center while avoiding obstacles and staying deterministic by prioritizing toward opponent's position to contest
    target_x = w // 2
    target_y = h // 2
    best_move = None
    best_score = 10**9
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny):
            continue
        # discourage moving into opponent's cell directly
        dist_to_target = cheb((nx, ny), (target_x, target_y))
        dist_to_opp = cheb((nx, ny), (ox, oy))
        score = dist_to_target * 2 + dist_to_opp  # deterministic weighting
        if score < best_score:
            best_score = score
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    # Fallback: stay
    return [0, 0]