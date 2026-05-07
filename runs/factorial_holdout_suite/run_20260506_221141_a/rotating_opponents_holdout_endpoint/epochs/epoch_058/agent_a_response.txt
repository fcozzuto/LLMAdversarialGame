def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Phase 1: take a resource we are at least as close to as the opponent.
    better = []
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        if sd <= od:
            better.append((sd, od, tx, ty))
    if better:
        better.sort(key=lambda t: (t[0], -t[1], t[2], t[3]))
        _, _, tx, ty = better[0]
    else:
        # Phase 2: contest by maximizing opponent advantage reduction (i.e., largest od - sd), tie by closest to us.
        contest = []
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            contest.append((od - sd, -sd, tx, ty))
        contest.sort(reverse=True, key=lambda t: (t[0], t[1], -t[2], -t[3]))
        _, _, tx, ty = contest[0]

    # Move one step toward target; avoid obstacles by considering alternatives.
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, tx, ty)
            moves.append((dist, abs(dx - dx0) + abs(dy - dy0), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda m: (m[0], m[1], m[2], m[3]))
    return [int(moves[0][2]), int(moves[0][3])]