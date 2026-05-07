def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or (0, 0)
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def clamp(x, lo, hi):
        return lo if x < lo else (hi if x > hi else x)

    sx, sy = clamp(sx, 0, w - 1), clamp(sy, 0, h - 1)
    ox, oy = clamp(ox, 0, w - 1), clamp(oy, 0, h - 1)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick best target deterministically: maximize relative advantage, then closeness.
    best = None
    for tx, ty in resources:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        val = (do - ds) * 1000 - ds
        if best is None or val > best[0] or (val == best[0] and (ds < best[1] or (ds == best[1] and (tx, ty) < best[2]))):
            best = (val, ds, (tx, ty))
    tx, ty = best[2]

    # Choose next step that reduces distance to target; break ties by opponent distance and then lexicographic move.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = md(nx, ny, tx, ty)
        no = md(nx, ny, ox, oy)
        # primary: minimize self distance to target
        # secondary: maximize opponent relative disadvantage after move
        adv = (md(nx, ny, ox, oy) - md(ox, oy, tx, ty))
        cand = (ns, -adv, no, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [int(best_move[3]), int(best_move[4])]