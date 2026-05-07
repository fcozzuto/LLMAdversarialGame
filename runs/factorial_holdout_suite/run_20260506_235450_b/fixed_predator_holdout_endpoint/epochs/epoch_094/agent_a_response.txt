def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def ti(v):
        try:
            return int(v)
        except:
            return 0

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = ti(sp[0]) if isinstance(sp, (list, tuple)) and len(sp) > 0 else 0, ti(sp[1]) if isinstance(sp, (list, tuple)) and len(sp) > 1 else 0
    ox, oy = ti(op[0]) if isinstance(op, (list, tuple)) and len(op) > 0 else 0, ti(op[1]) if isinstance(op, (list, tuple)) and len(op) > 1 else 0

    obs = set()
    for p in observation.get("obstacles") or []:
        x = y = None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
        elif isinstance(p, dict) and "x" in p and "y" in p:
            x, y = ti(p.get("x")), ti(p.get("y"))
        if x is not None and 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def cell_xy(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return ti(r[0]), ti(r[1])
        if isinstance(r, dict) and "x" in r and "y" in r:
            return ti(r.get("x")), ti(r.get("y"))
        return None

    def manh(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    targets = []
    for r in resources:
        t = cell_xy(r)
        if not t:
            continue
        x, y = t
        if not (0 <= x < w and 0 <= y < h):
            continue
        if (x, y) in obs:
            continue
        self_d = manh(sx, sy, x, y)
        opp_d = manh(ox, oy, x, y)
        # Prefer cells where we are relatively closer; break ties toward being closer ourselves.
        targets.append((opp_d - self_d, -self_d, x, y))
    if not targets:
        return [0, 0]
    _, _, tx, ty = max(targets)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_self = manh(nx, ny, tx, ty)
        # If opponent is close to the target, slightly prefer moves that increase our advantage.
        d_opp = manh(ox, oy, tx, ty)
        adv = d_opp - d_self
        # Lexicographic: maximize advantage, then minimize distance, then deterministic preference by move order.
        key = (adv, -d_self)
        if best is None or key > best:
            best, best_move = key, [dx, dy]
    return best_move