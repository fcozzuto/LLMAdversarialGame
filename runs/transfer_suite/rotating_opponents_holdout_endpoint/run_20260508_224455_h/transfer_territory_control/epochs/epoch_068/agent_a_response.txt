def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    opp_pos = observation.get("opponent_position", [7, 7])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def to_set(obj):
        s = set()
        for c in obj or []:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                s.add((int(c[0]), int(c[1])))
        return s

    un = to_set(observation.get("unclaimed_cells"))
    myt = to_set(observation.get("self_territory"))
    opt = to_set(observation.get("opponent_territory"))
    obst = to_set(observation.get("obstacles"))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    frontier = []
    for (x, y) in un:
        if ((x - 1, y) in opt) or ((x + 1, y) in opt) or ((x, y - 1) in opt) or ((x, y + 1) in opt):
            frontier.append((x, y))
    target = None
    if frontier:
        bestd = 10**9
        for t in frontier:
            d = man(sx, sy, t[0], t[1])
            if d < bestd:
                bestd = d
                target = t

    best = None
    best_key = None
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        adj_opt = False
        adj_un = False
        adj_my = False
        for ax, ay in neigh4:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in opt: adj_opt = True
            if (tx, ty) in un: adj_un = True
            if (tx, ty) in myt: adj_my = True

        gain = 0
        if (nx, ny) in un:
            gain += 3
        elif (nx, ny) in opt:
            gain += 6  # flipping on entry
        if adj_opt: gain += 2
        if adj_un: gain += 1
        if adj_my: gain += 1
        if (nx, ny) in myt: gain += 0

        # shaping: push toward opponent-side frontier when available, else toward unclaimed
        shape = 0
        if target is not None:
            shape = -man(nx, ny, target[0], target[1]) // 1
        else:
            if un:
                # approximate: prefer closer to nearest unclaimed by sampling a few
                dmin = 10**9
                count = 0
                for t in un:
                    d = man(nx, ny, t[0], t[1])
                    if d < dmin:
                        dmin = d
                    count += 1
                    if count > 20: break
                if dmin < 10**9:
                    shape = -dmin // 1
            else:
                shape = -man(nx, ny, ox, oy) // 1

        key = (gain + shape, -man(nx, ny, ox, oy), dx, dy)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]