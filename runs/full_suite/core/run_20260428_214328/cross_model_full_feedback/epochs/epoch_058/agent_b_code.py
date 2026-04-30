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

    # If there is a resource, head toward closest resource while avoiding obvious collision
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
        tx, ty = best
        dx = tx - sx; dx = -1 if dx < 0 else (1 if dx > 0 else 0)
        dy = ty - sy; dy = -1 if dy < 0 else (1 if dy > 0 else 0)
        # Try to move toward resource; if blocked, stay or sidestep away from opponent
        move = [dx, dy]
        nx, ny = sx + dx, sy + dy
        if (dx, dy) != (0, 0) and (nx, ny) in obst:
            move = [0, 0]
        # simple collision avoidance: if moving into opponent, prefer vertical/horizontal detour
        if (sx + move[0], sy + move[1]) == (ox, oy):
            if dy != 0:
                move = [0, 0]
            elif dx != 0:
                move = [0, 0]
        return move

    # If no resources, move towards opponent's corner to contest center
    tx = (w - 1) - ox
    ty = (h - 1) - oy
    dx = tx - sx; dx = -1 if dx < 0 else (1 if dx > 0 else 0)
    dy = ty - sy; dy = -1 if dy < 0 else (1 if dy > 0 else 0)
    mv = [dx, dy]
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obst:
        mv = [0, 0]
    if (sx + mv[0], sy + mv[1]) == (ox, oy):
        mv = [0, 0]
    return mv