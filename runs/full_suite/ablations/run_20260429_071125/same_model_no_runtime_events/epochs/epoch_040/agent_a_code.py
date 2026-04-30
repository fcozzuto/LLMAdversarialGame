def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Select a target we can reach earlier than the opponent, prioritizing resource availability.
    if resources:
        best = None
        best_key = None
        for tx, ty in resources:
            myd = kdist(sx, sy, tx, ty)
            od = kdist(ox, oy, tx, ty)
            # Prefer: larger lead for us; smaller distance for both (quick swing)
            key = (od - myd, -(myd + od), -abs(tx - sx) - abs(ty - sy), tx, ty)
            if best is None or key > best_key:
                best = (tx, ty)
                best_key = key
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    cur_cell = (sx, sy)
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        # Score higher is better.
        collect = 1 if (nx, ny) in resources else 0
        nd_my = kdist(nx, ny, tx, ty)
        nd_op = kdist(nx, ny, ox, oy)
        # Tie-break deterministically: prefer moves that keep us nearer target and farther from opponent.
        score = (collect * 1000, -nd_my, nd_op, -abs(nx - tx) - abs(ny - ty), -dx, -dy, nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]