def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    self_score = None
    opp_score = None
    sc = observation.get("scores")
    if isinstance(sc, (list, tuple)) and len(sc) >= 2:
        self_score, opp_score = sc[0], sc[1]
    elif isinstance(sc, dict):
        for k in ("self", "me", "player", "agent", "self_score"):
            if k in sc:
                self_score = sc[k]
                break
        for k in ("opponent", "opp", "enemy", "enemy_score", "opponent_score"):
            if k in sc:
                opp_score = sc[k]
                break

    try:
        self_score = float(self_score) if self_score is not None else None
    except Exception:
        self_score = None
    try:
        opp_score = float(opp_score) if opp_score is not None else None
    except Exception:
        opp_score = None

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def nearest_resource_dist2(x, y):
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            d = dist2(x, y, rx, ry)
            if best is None or d < best:
                best = d
        return best

    chase = False
    if self_score is not None and opp_score is not None:
        chase = self_score <= opp_score

    best_move = moves[4]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        val = 0
        rd = nearest_resource_dist2(nx, ny)
        if rd is not None:
            val += 1000 // (rd + 1)
        dop = dist2(nx, ny, ox, oy)
        if chase:
            val += -(dop)
        else:
            val += dop
        # small safety: prefer moves with more free neighbors
        mob = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if free(tx, ty):
                mob += 1