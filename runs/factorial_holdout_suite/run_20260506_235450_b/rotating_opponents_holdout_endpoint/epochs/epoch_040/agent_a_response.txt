def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def parse_xy(v):
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return None

    resources = []
    for r in observation.get("resources") or []:
        p = parse_xy(r)
        if not p:
            continue
        x, y = p
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # prefer closest for me; if tie, pick where I'm relatively closer than opponent
        key = (myd, -(myd - opd))
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # small obstacle-avoid tweak: if stepping onto obstacle, try alternate axis first deterministically
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # try X-only
        alt_dx, alt_dy = (1 if tx > sx else -1 if tx < sx else 0), 0
        nx2, ny2 = sx + alt_dx, sy + alt_dy
        if (0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles):
            return [alt_dx, alt_dy]
        # try Y-only
        alt_dx, alt_dy = 0, (1 if ty > sy else -1 if ty < sy else 0)
        nx2, ny2 = sx + alt_dx, sy + alt_dy
        if (0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles):
            return [alt_dx, alt_dy]
        # otherwise stay
        return [0, 0]

    return [dx, dy]