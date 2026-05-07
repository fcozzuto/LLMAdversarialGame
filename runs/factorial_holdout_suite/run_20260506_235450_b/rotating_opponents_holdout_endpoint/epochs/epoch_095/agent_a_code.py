def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    ap = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    def parse_pos(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict):
            if "x" in r and "y" in r:
                return int(r["x"]), int(r["y"])
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return None

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    blocked = set()
    for ob in (observation.get("obstacles") or []):
        p = parse_pos(ob) if not isinstance(ob, dict) else parse_pos(ob)
        if p is None:
            continue
        x, y = p
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    resources = observation.get("resources") or []
    best = None
    best_gap = -10**9
    nearest = None
    nearest_d = 10**9

    for r in resources:
        p = parse_pos(r)
        if p is None:
            continue
        x, y = p
        d1 = man(sx, sy, x, y)
        d2 = man(ox, oy, x, y)
        gap = d2 - d1
        if gap > best_gap or (gap == best_gap and (d1 < (nearest_d if nearest else 10**9))):
            best_gap = gap
            nearest = (x, y)
            nearest_d = d1

    if nearest is None:
        tx, ty = ox, oy
    else:
        tx, ty = nearest

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        myd = man(nx, ny, tx, ty)
        oppd = man(ox, oy, tx, ty)
        score = (oppd - myd) * 3 - myd
        if (dx, dy) == (0, 0):
            score -= 0.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]