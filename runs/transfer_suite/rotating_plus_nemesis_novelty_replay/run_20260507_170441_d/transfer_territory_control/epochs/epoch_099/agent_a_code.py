def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells") or []
    self_t = set(observation.get("self_territory") or [])
    opp_t = set(observation.get("opponent_territory") or [])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        x, y = a - c, b - d
        if x < 0: x = -x
        if y < 0: y = -y
        return x + y

    target = None
    if unclaimed:
        best = None
        for c in unclaimed:
            try:
                tx, ty = int(c[0]), int(c[1])
            except:
                continue
            if (tx, ty) in blocked:
                continue
            if not in_bounds(tx, ty):
                continue
            score = man(sx, sy, tx, ty)
            if best is None or score < best:
                best = score
                target = (tx, ty)

    if target is None:
        frontier = []
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in self_t and (nx, ny) not in opp_t and (nx, ny) not in blocked:
                frontier.append((nx, ny))
        if frontier:
            target = sorted(frontier)[0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        d_opp = man(nx, ny, ox, oy)
        if target is not None:
            d_tar = man(nx, ny, target[0], target[1])
            val = (-d_tar, d_opp, nx, ny)
        else:
            val = (0, d_opp, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]