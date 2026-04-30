def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

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
    if not resources:
        # fallback: move toward opponent-free center-ish
        tx, ty = w // 2, h // 2
        dx, dy = tx - sx, ty - sy
        return [(-1 if dx < 0 else (1 if dx > 0 else 0)), (-1 if dy < 0 else (1 if dy > 0 else 0))]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = None

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        my_d = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        op_d = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        # prefer closer to resources than opponent, also keep distance from opponent
        score = (op_d - my_d) * 1000 + my_d * (-1) + cheb(nx, ny, ox, oy) * 2
        if best_score is None or score > best_score or (score == best_score and (mx, my) < best_move):
            best_score = score
            best_move = (mx, my)

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]