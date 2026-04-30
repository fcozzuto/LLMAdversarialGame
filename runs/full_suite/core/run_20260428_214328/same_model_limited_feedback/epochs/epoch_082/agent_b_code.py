def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sp = observation.get('self_position', (0, 0))
    op = observation.get('opponent_position', (0, 0))
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    resources = observation.get('resources', []) or []
    obstacles_raw = observation.get('obstacles', []) or []
    obstacles = set()
    for o in obstacles_raw:
        try:
            obstacles.add((o[0], o[1]))
        except Exception:
            pass

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    resources = [tuple(r[:2]) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2]
    target = None
    best = None
    for rx, ry in resources:
        sd = cd(sx, sy, rx, ry)
        od = cd(ox, oy, rx, ry)
        val = (od - sd) * 10 - sd
        if best is None or val > best:
            best = val
            target = (rx, ry)

    best_move = None
    best_score = None
    if target is not None:
        rx, ry = target
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            ns = cd(nx, ny, rx, ry)
            os = cd(ox, oy, rx, ry)
            score = (os - ns) * 10 - ns
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            score = cd(nx, ny, ox, oy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move