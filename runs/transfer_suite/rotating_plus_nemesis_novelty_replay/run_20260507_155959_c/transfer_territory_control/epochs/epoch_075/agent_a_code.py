def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = observation.get("resources") or []
    best_target = None
    best_dist = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        tx, ty = int(r[0]), int(r[1])
        if not valid(tx, ty):
            continue
        d = abs(tx - sx) + abs(ty - sy)
        if best_dist is None or d < best_dist or (d == best_dist and (tx, ty) < best_target):
            best_dist = d
            best_target = (tx, ty)

    if best_target is None:
        best_target = (ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    chosen = (0, 0)
    chosen_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = abs(best_target[0] - nx) + abs(best_target[1] - ny)
        if chosen_score is None or score < chosen_score or (score == chosen_score and (dx, dy) < chosen):
            chosen_score = score
            chosen = (dx, dy)
    return [int(chosen[0]), int(chosen[1])]