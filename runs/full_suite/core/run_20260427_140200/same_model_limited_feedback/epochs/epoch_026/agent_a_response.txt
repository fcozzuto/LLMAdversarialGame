def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def add(x, y, dx, dy):
        return x + dx, y + dy

    if resources:
        best = None
        best_adv = None
        for rx, ry in resources:
            dself = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            adv = dop - dself  # positive if we are closer
            # tie-break toward nearer absolute distance
            if best_adv is None or adv > best_adv or (adv == best_adv and dself < best[0]):
                best_adv = adv
                best = (dself, rx, ry)
        _, tx, ty = best
        # If we're not advantaged anywhere, choose a resource closest to us but try to increase distance to opponent
        if best_adv is None or best_adv < 0:
            # find min our distance resource
            mind = None
            tx = resources[0][0]
            ty = resources[0][1]
            for rx, ry in resources:
                dself = cheb(sx, sy, rx, ry)
                if mind is None or dself < mind:
                    mind = dself
                    tx, ty = rx, ry
    else:
        # No resources: move toward center while avoiding opponent
        tx, ty = w//2, h//2

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = add(sx, sy, dx, dy)
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # score: prefer smaller distance to target, larger distance to opponent; strong penalty for illegal near-obs handled above
        score = d_to_opp * 0.8 - d_to_target
        if best_score is None or score > best_score or (score == best_score and (dx*dx + dy*dy) < (best_move[0]*best_move[0] + best_move[1]*best_move[1])):
            best_score = score
            best_move = (dx, dy)

    # If all moves blocked, deterministically stay
    return [int(best_move[0]), int(best_move[1])]