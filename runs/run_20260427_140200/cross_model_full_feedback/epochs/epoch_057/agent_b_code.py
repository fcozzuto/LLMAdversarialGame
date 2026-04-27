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

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Prefer moving toward closest resource if safe; otherwise flee from opponent or stay.
    best_dx, best_dy = 0, 0
    if resources:
        best_score = None
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            # candidate move toward resource
            dx = 0
            dy = 0
            if rx > sx: dx = 1
            elif rx < sx: dx = -1
            if ry > sy: dy = 1
            elif ry < sy: dy = -1
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # score: closer to resource and farther from opponent
            d_to_res = cheb(nx, ny, rx, ry)
            d_to_opp = cheb(nx, ny, ox, oy)
            score = -d_to_res*2 + d_to_opp
            if best_score is None or score > best_score:
                best_score = score
                best_dx, best_dy = dx, dy
        if best_score is not None:
            return [best_dx, best_dy]

    # No good resource path; move to maximize distance from opponent while staying safe
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        # prefer further from opponent, with tie-breaker staying still
        score = dist
        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy
    if best_score is None:
        return [0, 0]
    return [best_dx, best_dy]