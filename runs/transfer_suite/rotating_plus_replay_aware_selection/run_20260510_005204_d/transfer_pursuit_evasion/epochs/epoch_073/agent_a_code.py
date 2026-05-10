def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        pen = 0
        for i in (-1, 0, 1):
            xi = x + i
            if xi < 0 or xi >= w: 
                continue
            for j in (-1, 0, 1):
                yj = y + j
                if yj < 0 or yj >= h:
                    continue
                if (xi, yj) in blocked:
                    pen += 3 if (i == 0 and j == 0) else 1
        return pen

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if we_evader:
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        tx, ty = ox, oy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_goal = cheb(nx, ny, tx, ty)
        p = obst_pen(nx, ny)
        if we_evader:
            score = (d_opp * 2 - d_goal - p)
        else:
            score = (-d_goal * 2 - d_opp - p)
        key = (score, -dx, -dy)  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]