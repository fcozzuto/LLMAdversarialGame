def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (0, -1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    target = None
    if res:
        bestd = 10**18
        for x, y in res:
            if inb(x, y) and (x, y) not in obs:
                d = abs(x - sx) + abs(y - sy)
                if d < bestd:
                    bestd = d
                    target = (x, y)

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Score: prefer resources, avoid opponent, small center bias
        if target is not None:
            sdist = abs(target[0] - nx) + abs(target[1] - ny)
            score = -sdist * 10
        else:
            score = -(abs(nx - cx) + abs(ny - cy))
        odist = abs(ox - nx) + abs(oy - ny)
        score += odist * 2
        # If moving onto a resource cell, boost
        if (nx, ny) in set(res):
            score += 1000
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move