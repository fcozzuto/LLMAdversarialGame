def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    # Choose target: if opponent is clearly closer to some resource, contest that.
    # Otherwise go for a resource we are closer to.
    best_contest = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd  # positive => we are closer; negative => opponent is closer
        # contest if opponent closer by at least 1
        if gap <= -1:
            # pick most negative gap (opponent much closer), tie by our distance then position
            key = (gap, sd, rx, ry)
            if best_contest is None or key < best_contest[0]:
                best_contest = (key, (rx, ry))
    if best_contest is not None:
        target = best_contest[1]
    else:
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (-sd, (od - sd), rx, ry)  # prefer larger sd? no: negative sd -> smallest sd
            key = (sd, (od - sd), rx, ry)  # smallest sd; if tie, smaller (od-sd) means we are relatively closer
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1]

    tx, ty = target

    # Greedy step toward target with obstacle avoidance and light opponent-pressure.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # If we can reduce our distance, do it; also slightly prefer moves that make it harder for opponent.
        # Add a small deterministic tie-break by position.
        score = (d_self, -d_opp, nx, ny)
        if best_move is None or score < best_move[0]:
            best_move = (score, [dx, dy])

    return best_move[1]