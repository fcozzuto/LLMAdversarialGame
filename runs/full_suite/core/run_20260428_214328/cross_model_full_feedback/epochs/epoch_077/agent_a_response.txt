def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    me = (sx, sy)
    them = (ox, oy)

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = None
        best_key = None
        for r in resources:
            myd = cheb(me, r)
            opd = cheb(them, r)
            # prioritize stealing: (opd - myd), then shorter my distance, then deterministic coord tie
            key = (-(opd - myd), myd, r[0], r[1])
            if best_key is None or key < best_key:
                best_key = key
                best = r
        return best

    tx, ty = best_target()

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    cur = me
    cur_dist = cheb(cur, (tx, ty))
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb((nx, ny), (tx, ty))
        opd = cheb(them, (tx, ty))
        # move score: prefer decreasing my distance; if tie, keep opponent further in relative race
        # (use opd-from-move as proxy by comparing myd vs constant opd)
        score = (myd, opd - myd, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move == [0, 0] and resources:
        # if blocked, fallback to any valid step that reduces distance to the chosen target
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and cheb((nx, ny), (tx, ty)) < cur_dist:
                return [dx, dy]

    return best_move