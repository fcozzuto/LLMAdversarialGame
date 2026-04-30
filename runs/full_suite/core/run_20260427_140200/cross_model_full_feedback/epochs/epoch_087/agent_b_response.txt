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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = -10**9

    # Core heuristic: head toward nearest resource while staying reasonably distant from opponent.
    if resources:
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # compute distance to closest resource after move
            best_r = None
            best_r_dist = 10**9
            for rx, ry in resources:
                d = dist((nx, ny), (rx, ry))
                if d < best_r_dist:
                    best_r_dist = d
                    best_r = (rx, ry)
            if best_r is None:
                continue
            # distance to opponent after move
            opp_dist = dist((nx, ny), (ox, oy))
            # score: closer to resource and farther from opponent
            score = -best_r_dist * 2 + opp_dist
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # No resources visible; simple pursuit: move toward center while keeping away from opponent
        dx = 0
        dy = 0
        if mx < center[0]:
            dx = 1
        elif mx > center[0]:
            dx = -1
        if my < center[1]:
            dy = 1
        elif my > center[1]:
            dy = -1
        # adjust to avoid obstacle or stay in bounds
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            best_move = (0, 0)
        else:
            best_move = (dx, dy)

        return [best_move[0], best_move[1]]

    return [best_move[0], best_move[1]]