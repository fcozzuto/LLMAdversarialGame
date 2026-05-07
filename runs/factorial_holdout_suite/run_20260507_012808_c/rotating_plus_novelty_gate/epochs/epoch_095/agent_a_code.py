def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

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

    even_turn = (int(observation.get("turn_index") or 0) % 2 == 0)

    best = None
    for tx, ty in resources:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        if even_turn:
            # Chase resources we can reach earlier (max advantage).
            key = (do - ds, -ds, -abs(tx - ox) - abs(ty - oy), tx, ty)
        else:
            # Deny: go toward the resource the opponent is closest to (even if not best for us).
            key = (-do, ds, abs(tx - sx) + abs(ty - sy), tx, ty)
        if best is None or key > best:
            best = key
            target = (tx, ty)

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try axis-only alternatives deterministically.
        ax = (sx + dx, sy)
        ay = (sx, sy + dy)
        if ax not in obstacles:
            dx, dy = dx, 0
        elif ay not in obstacles:
            dx, dy = 0, dy
        else:
            # Try one-step toward the other coordinate only if free.
            dx, dy = 0, 0

    return [int(dx), int(dy)]