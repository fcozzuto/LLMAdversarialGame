def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = abs(ax - bx), abs(ay - by)
        return dx if dx > dy else dy

    def target_score(t):
        self_d = cheb((sx, sy), t)
        opp_d = cheb((ox, oy), t)
        # Prefer resources we can reach earlier; if tied, prefer farther from opponent to reduce denial impact.
        return ((opp_d - self_d), (-opp_d), (-self_d), -((t[0] + 1) * 1000 + (t[1] + 1)))

    target = resources[0]
    bestk = None
    for t in resources:
        k = target_score(t)
        if bestk is None or k > bestk:
            bestk = k
            target = t

    tx, ty = target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                nd = cheb((nx, ny), (tx, ty))
                opp_nd = cheb((nx, ny), (ox, oy))
                # Prefer reducing distance to target; if similar, keep away from opponent slightly.
                moves.append(((-nd), (opp_nd), (abs(dx) + abs(dy)), dx, dy))
    moves.sort()

    # If no valid move (should be rare), stay.
    if not moves:
        return [0, 0]

    _, _, _, dx, dy = moves[0]
    return [int(dx), int(dy)]