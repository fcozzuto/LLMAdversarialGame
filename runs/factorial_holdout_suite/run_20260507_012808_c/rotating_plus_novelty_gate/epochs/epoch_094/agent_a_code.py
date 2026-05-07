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
        x, y = p[0], p[1]
        try:
            x = int(x); y = int(y)
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

    # Prefer cells we can reach earlier; tie-break by maximizing opponent disadvantage and closeness.
    best = None
    for tx, ty in resources:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        if do <= ds:
            # Strong preference for "steal/secure" targets where we are closer.
            # If equal, go for nearest ours to reduce time-to-collect.
            key = (0, ds, -do, tx, ty)
        else:
            # Still allow if no secure targets exist; penalize targets opponent can reach first.
            key = (1, do - ds, ds, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))

    tx, ty = best[1]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Small bias to avoid stepping into obstacles if target cell is blocked (rare, but keep safe).
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try axis-aligned alternative deterministically.
        alt = [(dx, 0), (0, dy), (0, 0)]
        for adx, ady in alt:
            if 0 <= sx + adx < w and 0 <= sy + ady < h and (sx + adx, sy + ady) not in obstacles:
                return [adx, ady]
        return [0, 0]

    return [dx, dy]