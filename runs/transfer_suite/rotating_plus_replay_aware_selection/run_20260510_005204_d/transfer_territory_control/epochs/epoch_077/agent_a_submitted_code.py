def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    nbrs = [(sx+dx, sy+dy, dx, dy) for dx, dy in dirs if ok(sx+dx, sy+dy)]
    if not nbrs:
        return [0, 0]

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                targets.append((x, y))
    if not targets:
        for p in observation.get("resources") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if ok(x, y):
                    targets.append((x, y))
            if len(targets) >= 50:
                break

    if targets:
        best_t = targets[0]
        best_d = cd(sx, sy, best_t[0], best_t[1])
        for x, y in targets[1:]:
            d = cd(sx, sy, x, y)
            if d < best_d:
                best_d = d
                best_t = (x, y)
        tx, ty = best_t
        best_move = (0, 0)
        best_score = None
        for nx, ny, dx, dy in nbrs:
            sd = cd(nx, ny, tx, ty)
            od = cd(nx, ny, ox, oy)
            score = (sd, -od, -dx, -dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_move = (0, 0)
    best_score = None
    for nx, ny, dx, dy in nbrs:
        score = (-cd(nx, ny, ox, oy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1]]]