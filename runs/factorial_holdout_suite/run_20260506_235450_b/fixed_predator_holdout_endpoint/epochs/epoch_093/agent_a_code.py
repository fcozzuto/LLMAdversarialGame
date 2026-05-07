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
    sx = ti(sp[0]) if isinstance(sp, (list, tuple)) and len(sp) > 0 else 0
    sy = ti(sp[1]) if isinstance(sp, (list, tuple)) and len(sp) > 1 else 0
    ox = ti(op[0]) if isinstance(op, (list, tuple)) and len(op) > 0 else 0
    oy = ti(op[1]) if isinstance(op, (list, tuple)) and len(op) > 1 else 0

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
        elif isinstance(p, dict) and "x" in p and "y" in p:
            x, y = ti(p.get("x")), ti(p.get("y"))
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources") or []
    best = None
    best_key = None

    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = ti(r.get("x")), ti(r.get("y"))
        else:
            continue
        if not (0 <= x < w and 0 <= y < h) or (x, y) in obs:
            continue
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        adv = od - sd
        key = (-adv, sd, -(x + y), x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    if best is None:
        dx, dy = 0, 0
        for x, y in ((sx - 1, sy), (sx + 1, sy), (sx, sy - 1), (sx, sy + 1)):
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                dx, dy = x - sx, y - sy
                break
        return [dx, dy]

    tx, ty = best
    candidates = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        od = abs(tx - ox) + abs(ty - oy)
        my_adv = od - nd
        score = (-my_adv, nd, nx + ny, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move