def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    resources = []
    resset = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))
                resset.add((x, y))

    if (sx, sy) in resset:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        # Choose a resource where we are relatively closer than the opponent.
        best_rx, best_ry = resources[0]
        best_gain = cheb(ox, oy, resources[0][0], resources[0][1]) - cheb(sx, sy, resources[0][0], resources[0][1])
        for rx, ry in resources[1:]:
            gain = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
            if gain > best_gain:
                best_gain = gain
                best_rx, best_ry = rx, ry
        tx, ty = best_rx, best_ry
    else:
        # No visible resources: move to reduce distance to opponent and avoid obstacles (deterministic).
        tx, ty = ox, oy

    best_move = legal[0]
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Main: get closer to target; Secondary: deny opponent by preferring states where we're much closer than them.
        # Tertiary: slightly keep away from opponent to reduce interception.
        score = (do - ds) * 1000 - ds * 3 - cheb(nx, ny, ox, oy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]