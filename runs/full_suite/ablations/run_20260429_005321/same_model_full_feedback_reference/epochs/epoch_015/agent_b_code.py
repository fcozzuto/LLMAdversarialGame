def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    target = None
    if resources:
        best = None
        for r in resources:
            myd = md(me, r)
            opd = md(opp, r)
            # Prefer resources where opponent is farther than us; break ties deterministically.
            sc = opd - myd
            cand = (sc, -myd, -r[0], -r[1])
            if best is None or cand > best[0]:
                best = (cand, r)
        target = best[1]
    else:
        # No visible resources: move to a corner farther from opponent.
        corners = [(0, 0), (w - 1, h - 1), (0, h - 1), (w - 1, 0)]
        target = max(corners, key=lambda c: (md(me, c) - md(opp, c), c[0], c[1]))

    best_move = valid[0]
    best_score = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        nd_target = md((nx, ny), target)
        nd_opp = md((nx, ny), opp)
        # Tradeoff: close to target, stay away from opponent to reduce contest.
        score = (-2 * nd_target) + (1 * nd_opp)
        # Slight deterministic bias to keep movement stable: prefer staying or moving toward target direction.
        score += (0 if dx == 0 and dy == 0 else 0)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]