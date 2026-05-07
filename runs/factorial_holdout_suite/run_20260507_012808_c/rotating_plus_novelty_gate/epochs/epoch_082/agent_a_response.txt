def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
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

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny
    def man(a,b,c,d): return abs(a-c) + abs(b-d)

    if not resources:
        for dx, dy in [(1,0),(1,1),(0,1),(1,-1),(0,0),(0,-1),(-1,0),(-1,-1),(-1,1)]:
            nx, ny = clamp(sx+dx, sy+dy)
            if (nx, ny) not in obstacles:
                return [int(nx-sx), int(ny-sy)]
        return [0, 0]

    # pick a contested "best" target deterministically
    best_t = None
    best_key = None
    for tx, ty in resources:
        self_d = man(sx, sy, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Prefer winning race; if similar, prefer closer and then lexicographic
        key = (self_d - 0.85 * opp_d, self_d, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    # score each move by immediate safety + progress toward target
    best_m = None
    best_v = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        nd = man(nx, ny, tx, ty)
        od = man(nx, ny, ox, oy)
        # bonus for reducing distance to target and making opponent farther
        v = (nd - 1.05 * od, nd, abs((nx - sx)) + abs((ny - sy)), nx, ny)
        if best_v is None or v < best_v:
            best_v = v
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]