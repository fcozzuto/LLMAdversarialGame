def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or (0, 0)
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

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If we can grab immediately, do it (strong deterministic step).
    adj = []
    for tx, ty in resources:
        if dist(sx, sy, tx, ty) == 0:
            return [0, 0]
        if max(abs(tx - sx), abs(ty - sy)) == 1 and (sx, sy) != (tx, ty):
            adj.append((tx, ty))
    if adj:
        best = None
        best_key = None
        for tx, ty in adj:
            key = (dist(ox, oy, tx, ty) - dist(sx, sy, tx, ty), -dist(sx, sy, tx, ty), -tx, -ty)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
        return [0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1)]

    # Otherwise, choose the resource we can arrive at earliest relative to the opponent.
    best = None
    best_key = None
    for tx, ty in resources:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        key = (do - ds, -ds)  # maximize relative lead; then prefer closer
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Step greedily toward target, but ensure we don't step onto obstacles.
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy))
    if not cand:
        return [0, 0]

    # Prefer moves that reduce distance to target and increase relative advantage vs opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        ds2 = dist(nx, ny, tx, ty)
        do2 = dist(ox, oy, tx, ty)
        val = ((do2 - ds2), (-ds2), -(abs((tx - nx)) + abs((ty - ny))), -(dx * dx + dy * dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]