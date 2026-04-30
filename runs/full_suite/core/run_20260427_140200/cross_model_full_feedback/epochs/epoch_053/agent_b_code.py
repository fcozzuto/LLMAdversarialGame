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

    # If there are resources, try to move toward the closest one while avoiding collision with opponent
    if resources:
        best_rx, best_ry = None, None
        best_score = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # prefer resources where we are closer than opponent (advantage)
            ahead = d_op - d_me
            dist_bias = -d_me
            score = (1 if ahead > 0 else 0) * 1000 + dist_bias
            if best_score is None or score > best_score:
                best_score = score
                best_rx, best_ry = rx, ry

        tx = best_rx
        ty = best_ry
        dx = 0
        dy = 0
        if sx < tx: dx = 1
        elif sx > tx: dx = -1
        if sy < ty: dy = 1
        elif sy > ty: dy = -1
        if legal(sx + dx, sy + dy):
            return [dx, dy]
        # if blocked, try to step around the resource
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                nx, ny = sx + adx, sy + ady
                if legal(nx, ny):
                    return [adx, ady]
        return [0, 0]

    # No resources: simple pursuit of center while dodging obstacles and opponent
    cx, cy = w // 2, h // 2
    dx = 0
    dy = 0
    if sx < cx: dx = 1
    elif sx > cx: dx = -1
    if sy < cy: dy = 1
    elif sy > cy: dy = -1

    if legal(sx + dx, sy + dy):
        return [dx, dy]

    # try alternative moves
    for adx in (-1, 0, 1):
        for ady in (-1, 0, 1):
            if adx == 0 and ady == 0:
                continue
            nx, ny = sx + adx, sy + ady
            if legal(nx, ny):
                return [adx, ady]

    return [0, 0]