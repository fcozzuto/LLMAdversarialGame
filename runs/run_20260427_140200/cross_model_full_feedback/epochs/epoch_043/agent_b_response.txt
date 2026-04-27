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

    def dist_manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def dist_sq(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Target strategy: pick resource that maximizes lead difference (opp distance to resource minus me distance),
    # breaking ties by closer distance to resource. If no resources, head toward a corner away from opponent.
    if resources:
        best_move = (0, 0)
        best_score = None
        best_target = None
        for rx, ry in resources:
            d_me = dist_manh((sx, sy), (rx, ry))
            d_opp = dist_manh((ox, oy), (rx, ry))
            lead = d_opp - d_me  # want positive lead
            dist_to = d_me
            score = (lead, -dist_to)
            if best_score is None or score > best_score:
                best_score = score
                best_target = (rx, ry)
        if best_target is not None:
            tx, ty = best_target
            # choose move that moves towards target
            best_dx = 0
            best_dy = 0
            best_td = None
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not legal(nx, ny):
                    continue
                td = abs(nx - tx) + abs(ny - ty)
                if best_td is None or td < best_td:
                    best_td = td
                    best_dx, best_dy = dx, dy
            return [best_dx, best_dy]

    # Fallback: move away from opponent if possible, else step toward center
    best_dx = 0
    best_dy = 0
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # prefer increasing distance from opponent
        d = dist_manh((nx, ny), (ox, oy))
        if best_score is None or d > best_score:
            best_score = d
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]