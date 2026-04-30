def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if inb(x, y):
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if inb(x, y) and (x, y) not in obstacles:
            resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        # deterministically drift toward center while respecting opponent pressure
        target = (w // 2, h // 2)
        best = None
        best_score = None
        for dx, dy, nx, ny in legal:
            score = cheb((nx, ny), target) - 0.2 * cheb((nx, ny), (ox, oy))
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move that secures a resource by maximizing (opponent_reach - self_reach),
    # then minimize self distance to that resource; also bias away from becoming too close to opponent.
    best_move = (0, 0)
    best_tuple = None
    for dx, dy, nx, ny in legal:
        dself_to_opp = cheb((nx, ny), (ox, oy))
        best_res_tuple = None
        for rx, ry in resources:
            dres_self = cheb((nx, ny), (rx, ry))
            dres_opp = cheb((ox, oy), (rx, ry))
            # prefer states where we arrive strictly earlier; if tied, be closer
            t = (dres_self - dres_opp, dres_self, -dres_opp)
            if best_res_tuple is None or t < best_res_tuple:
                best_res_tuple = t
        # convert to overall preference: smallest (self-opp), then self distance, then avoid opponent too much
        overall = (best_res_tuple[0], best_res_tuple[1], -dself_to_opp)
        if best_tuple is None or overall < best_tuple:
            best_tuple = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]