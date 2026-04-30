def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def clamp(nx, ny):
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        return nx, ny

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target():
        if not resources:
            return None
        best = None
        bestv = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dv = dist((sx, sy), (rx, ry)) - 0.25 * dist((ox, oy), (rx, ry))
            if best is None or dv < bestv:
                bestv = dv
                best = (rx, ry)
        return best

    target = best_target()
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        if target is None:
            tx, ty = nx, ny
            ourd = 0
            oppd = dist((ox, oy), (tx, ty))
        else:
            tx, ty = target
            ourd = dist((nx, ny), (tx, ty))
            oppd = dist((ox, oy), (tx, ty))
            # If opponent could be closer after our move, slightly penalize
            oppd_after = oppd
        score = 0
        if (nx, ny) in resources:
            score += 1000  # strongly prefer taking resource
        score += -ourd
        if target is not None:
            score += 0.1 * (oppd_after - oppd)  # keep deterministic tie behavior
            score += 0.02 * (-dist((nx, ny), target))  # small regularization
        # Mild preference to not step away from corner direction: helps consistency
        score += -0.001 * dist((nx, ny), (0, 0))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if (sx + best_move[0], sy + best_move[1]) in obstacles:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]