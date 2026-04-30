def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = 1 if sx < cx else (-1 if sx > cx else 0)
        dy = 1 if sy < cy else (-1 if sy > cy else 0)
        return [dx, dy]

    deltas = [[0,0],[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1]]
    best_delta = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            score = -10**15
        else:
            min_near = 10**9
            for ox2, oy2 in obs:
                d = cheb(nx, ny, ox2, oy2)
                if d < min_near:
                    min_near = d
            obstacle_pen = (0 if min_near > 1 else (3 - min_near) * 5)

            # Choose the resource that gives maximum advantage after this move.
            adv_best = -10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Encourage grabbing close to us, while denying opponent.
                adv = (do - ds) * 20 - ds
                if adv > adv_best:
                    adv_best = adv
            score = adv_best - obstacle_pen - cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0) * 0.2

        if score > best_score:
            best_score = score
            best_delta = [dx, dy]

    return [int(best_delta[0]), int(best_delta[1])]