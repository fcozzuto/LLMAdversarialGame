def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    t = int(observation.get("turn_index", 0))
    dirs = dirs[t % 9:] + dirs[:t % 9]
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)
    targets = observation.get("unclaimed_cells") or []
    if not targets:
        targets = []
        for k in ("resources", "remaining_resources"):
            if observation.get(k):
                targets = observation[k]
                break
    if not targets:
        return [0, 0] if inside(sx, sy) and (sx, sy) not in obstacles else [0, 0]
    best = None
    bs = -10**18
    for tx, ty in targets:
        x, y = int(tx), int(ty)
        if not inside(x, y) or (x, y) in obstacles:
            continue
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        sc = (ds == 0 and 10**9) + (do - ds) * 1000 - (abs(x - (w - 1) / 2) + abs(y - (h - 1) / 2))
        if sc > bs:
            bs = sc
            best = (x, y)
    if best is None:
        return [0, 0]
    tx, ty = best
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        val = (opd - myd) * 1000 - myd - (dx != 0 or dy != 0)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]