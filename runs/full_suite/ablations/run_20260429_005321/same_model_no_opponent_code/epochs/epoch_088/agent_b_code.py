def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    alpha = 0.35  # prefer resources opponent is less able to reach quickly
    best_t = None
    best_score = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        score = ds - alpha * do
        if best_score is None or score < best_score or (score == best_score and (ds, do) < (cheb(sx, sy, best_t[0], best_t[1]), cheb(ox, oy, best_t[0], best_t[1]))):
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t
    cur_r = cheb(sx, sy, tx, ty)
    cur_o = cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_h = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nr = cheb(nx, ny, tx, ty)
        # small penalty for moving away; mild bias to keep progressing while not suicidally near opponent
        nh = nr - alpha * cur_o + (2 if nr > cur_r else 0) + (0.05 * cheb(nx, ny, ox, oy))
        if best_h is None or nh < best_h:
            best_h = nh
            best_move = [dx, dy]

    return best_move