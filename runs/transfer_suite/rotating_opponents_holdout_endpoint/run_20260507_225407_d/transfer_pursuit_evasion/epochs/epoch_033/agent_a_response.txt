def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "")
    opp_role = str(observation.get("opponent_role", "") or "")
    if "evader" in self_role.lower() and "pursuer" in opp_role.lower():
        role = "evader"
    elif "pursuer" in self_role.lower() and "evader" in opp_role.lower():
        role = "pursuer"
    else:
        scores = observation.get("scores", {})
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0))) or 0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0))) or 0
        elif isinstance(scores, (list, tuple)) and len(scores) >= 2:
            my_s, op_s = scores[0] or 0, scores[1] or 0
        else:
            my_s = observation.get("self_score", 0) or 0
            op_s = observation.get("opponent_score", 0) or 0
        role = "pursuer" if my_s <= op_s else "evader"

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if role == "pursuer":
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            key = (v, dx, dy)
            if best is None or key < bestv:
                bestv = key
                best = (dx, dy)
        if best is None:
            best = (0, 0)
        return [best[0], best[1]]

    # evader: flee to a corner maximizing distance from pursuer, avoid obstacles
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = corners[0]
    best_tc = None
    for c in corners:
        tc = cheb(c[0], c[1], ox, oy)
        key = (-tc, c[0], c[1])
        if best_tc is None or key < best_tc:
            best_tc = key
            target = c

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # prioritize increasing distance from opponent, then getting closer to chosen corner
        d_opp = cheb(nx, ny, ox, oy)
        d_t = cheb(nx, ny, target[0], target[1])
        key = (-d_opp, d_t, dx, dy)
        if best is None or key < bestv:
            bestv = key
            best = (dx, dy)
    if best is None:
        best = (0, 0)
    return [best[0], best[1]]