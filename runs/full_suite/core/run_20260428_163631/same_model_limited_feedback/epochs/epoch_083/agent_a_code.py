def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obst = set((x, y) for x, y in obstacles)
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    if resources:
        best = None; bestv = -10**9
        for rx, ry in resources:
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            v = (opd - myd) * 100 - myd  # prefer resources I'm closer to
            if v > bestv:
                bestv = v; best = (rx, ry)
            elif v == bestv and best is not None:
                # deterministic tie-break: lower myd then lexicographic
                cb = dist((sx, sy), best)
                if myd < cb or (myd == cb and (rx, ry) < best):
                    best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w//2, h//2)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    cur_best = None; cur_bdist = 10**9; cur_bord = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obst:
            continue
        d = dist((nx, ny), (tx, ty))
        bord = (abs(nx-(tx)) + abs(ny-(ty)))  # secondary
        if d < cur_bdist or (d == cur_bdist and bord < cur_bord) or (d == cur_bdist and bord == cur_bord and (dx, dy) < cur_best):
            cur_best = (dx, dy); cur_bdist = d; cur_bord = bord
    if cur_best is None:
        return [0, 0]
    return [cur_best[0], cur_best[1]]