def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict):
            pos = r.get("pos", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            else:
                x = r.get("x", None)
                y = r.get("y", None)
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not ok(sx, sy):
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))

    best = (0, 0)
    best_score = -10**9
    have_res = len(resources) > 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if have_res:
            mind = 10**9
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if d < mind: mind = d
            score += 1000 - mind * 20
        else:
            score += dist(nx, ny, ox, oy) * 2  # drift away if no resources known
        score += (dist(nx, ny, ox, oy) < dist(sx, sy, ox, oy)) * (-30)  # avoid moving closer
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best_score == -10**9:
        return [0, 0]
    return [best[0], best[1]]