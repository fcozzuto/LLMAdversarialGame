def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1), (0,-1), (1,-1),
              (-1, 0), (0,0), (1,0),
              (-1,1), (0,1), (1,1)]

    # valid moves not colliding with obstacles
    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0,0]

    # helper metrics
    def cheb(a, b):
        ax, ay = a
        bx, by = b
        return max(abs(ax-bx), abs(ay-by))

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    center = (w//2, h//2)
    best_move = None
    best_score = None

    # If resources exist, prioritize moving toward nearest resource while keeping some distance from opponent
    if resources:
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            # nearest resource distance after move
            nd = min(dist((nx, ny), r) for r in resources)
            # distance to opponent after move
            od = dist((nx, ny), (ox, oy))
            # current distance to opponent
            cur_od = dist((sx, sy), (ox, oy))
            # prefer reducing distance to resource and not moving into immediate threat
            score = (-nd) - max(0, od - cur_od)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return list(best_move) if best_move is not None else [0,0]

    # No resources: head toward center while staying away from opponent
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        to_center = cheb((nx, ny), center)
        to_opp = cheb((nx, ny), (ox, oy))
        cur_center = cheb((sx, sy), center)
        cur_opp = cheb((sx, sy), (ox, oy))
        score = (-(to_center - cur_center)) - (to_opp - cur_opp)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return list(best_move) if best_move is not None else [0,0]