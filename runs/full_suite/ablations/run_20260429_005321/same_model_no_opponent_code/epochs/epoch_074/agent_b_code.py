def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    want = resources[0] if resources else (ox, oy)

    def best_resource_from(x, y):
        if not resources:
            return None, 0
        best_d, best_xy = None, None
        for rx, ry in resources:
            if best_d is None or dist2(x, y, rx, ry) < best_d:
                best_d, best_xy = dist2(x, y, rx, ry), (rx, ry)
        return best_xy, best_d

    target, _ = best_resource_from(sx, sy)
    tx, ty = target if target is not None else (ox, oy)

    best_move, best_score = (0, 0), None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if resources:
            tr = (nx, ny) in resources
            my = min(dist2(nx, ny, rx, ry) for rx, ry in resources) if resources else 10**9
            op = min(dist2(ox, oy, rx, ry) for rx, ry in resources) if resources else 10**9
            score = (1000000 if tr else 0) + (op - my) * 10 - my
        else:
            my = dist2(nx, ny, tx, ty)
            op = dist2(ox, oy, tx, ty)
            score = (op - my) * 10 - my
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move