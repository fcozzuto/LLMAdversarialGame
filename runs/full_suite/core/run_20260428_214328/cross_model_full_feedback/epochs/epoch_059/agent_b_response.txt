def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def dist_cheb(a, b):
        dx = abs(a[0]-b[0]); dy = abs(a[1]-b[1])
        return dx if dx>dy else dy

    # Heuristic: if resources exist, move toward closest; else approach center while avoiding obstacle
    target = None
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            score = (d, od)
            if best_score is None or score < best_score:
                best = (rx, ry)
                best_score = score
        target = best
    else:
        target = (w//2, h//2)

    tx, ty = target if target is not None else (sx, sy)

    # Choose move toward target with simple collision avoidance
    best_move = None
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny): 
                continue
            if (nx, ny) in obst:
                continue
            # Avoid landing on opponent
            if nx == ox and ny == oy:
                continue
            d = dist_cheb((nx, ny), (tx, ty))
            od = dist_cheb((nx, ny), (ox, oy))
            score = (d, od)
            if best_score is None or score < best_score:
                best_move = (dx, dy)
                best_score = score

    if best_move is None:
        # Try any valid non-obstacle move, else stay
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inside(nx, ny): 
                    continue
                if (nx, ny) in obst:
                    continue
                if nx == ox and ny == oy:
                    continue
                best_move = (dx, dy)
                break
            if best_move is not None:
                break

    if best_move is None:
        best_move = (0, 0)

    dx, dy = best_move
    return [dx, dy]