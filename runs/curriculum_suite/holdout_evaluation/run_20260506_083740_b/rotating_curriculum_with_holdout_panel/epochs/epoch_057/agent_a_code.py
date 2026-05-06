def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Drift toward center while staying safe
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = (nx - cx) ** 2 + (ny - cy) ** 2
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    best_target = None
    best_score = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        d_me = md(sx, sy, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        if d_me == 0:
            # Prefer immediate collection
            return [0, 0]
        # Resource denial: strongly favor targets where we can arrive strictly before opponent
        arrival_adv = d_opp - d_me
        reach_block = 1 if d_opp <= d_me else 0
        # Small tie-breaker: prefer closer resources
        tscore = (arrival_adv * 1000) - reach_block * 600 - d_me * 3
        if best_score is None or tscore > best_score or (tscore == best_score and d_me < md(sx, sy, best_target[0], best_target[1]) if best_target else True):
            best_score = tscore
            best_target = (rx, ry)

    rx, ry = best_target
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Choose next step that maximizes (opponent distance advantage after move) while approaching target
    best = [0, 0]
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me2 = md(nx, ny, rx, ry)
        d_opp2 = md(ox, oy, rx, ry)
        # Center bias to reduce oscillation
        center_pen = ((nx - cx) ** 2 + (ny - cy) ** 2) * 0.001
        # If opponent is close, prioritize moves that increase distance to their potential snatch point
        opp_threat = 0
        for r in resources:
            if r and len(r) >= 2:
                tx, ty = int(r[0]), int(r[1])
                if valid(tx, ty):
                    opp_threat = max(opp_threat, md(ox, oy, tx, ty) - md(nx, ny, tx, ty))
        v = (d_opp2 - d_me2) * 1000 - d_me2 * 5 + center_pen + (opp_threat * 0.1)
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    return best