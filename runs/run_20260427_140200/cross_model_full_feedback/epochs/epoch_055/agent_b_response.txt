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

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # simple priority: go to closest resource if safe, else move to position maximizing distance from opponent
    best_dx, best_dy = 0, 0
    if resources:
        best_score = None
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            dod = cheb(ox, oy, rx, ry)
            score = -dme  # closer to resource is better
            # discourage approaching opponent to resource
            if dod <= dme:
                score -= 1
            if best_score is None or score > best_score:
                best_score = score
                best_target = (rx, ry)
        tx, ty = best_target
        # move towards target with limited delta
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if legal(sx + dx, sy + dy):
            return [dx, dy]
        # fallback try to step towards target with alternative axis
        if legal(sx + dx, sy):
            return [dx, 0]
        if legal(sx, sy + dy):
            return [0, dy]
        # if blocked, stay
        return [0, 0]

    # no resources: head away from opponent and toward corner farthest from opp
    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_score = None
    best_move = (0,0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist_opp = cheb(nx, ny, ox, oy)
        dist_corner = max(abs((w-1) - nx), abs((h-1) - ny))
        score = dist_corner - dist_opp
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]