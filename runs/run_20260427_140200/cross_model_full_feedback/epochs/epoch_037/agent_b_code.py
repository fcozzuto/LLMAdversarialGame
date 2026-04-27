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

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Simple deterministic priority:
    # 1) If there is a resource not adjacent, move towards closest resource.
    # 2) If adjacent to resource or none, move to maximize distance from opponent or block.
    best_dx = 0
    best_dy = 0
    best_score = None

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # score: distance to closest resource (minimize), tie-break by staying away from opponent
            d_to_r = None
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d_to_r is None or d < d_to_r:
                    d_to_r = d
            d_from_opp = man(nx, ny, ox, oy)
            score = (d_to_r if d_to_r is not None else 0, -d_from_opp)
            if best_score is None or score < best_score:
                best_score = score
                best_dx, best_dy = dx, dy
    else:
        # No resources visible: move to increase distance from opponent (avoid trap)
        # choose move that maximizes distance to opponent; deterministic by exploring dirs in order
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_from_opp = man(nx, ny, ox, oy)
            score = (-d_from_opp)
            if best_score is None or score < best_score:
                best_score = score
                best_dx, best_dy = dx, dy

    # If somehow no move chosen (shouldn't happen), stay.
    if best_dx is None or best_dy is None:
        return [0, 0]
    return [int(best_dx), int(best_dy)]