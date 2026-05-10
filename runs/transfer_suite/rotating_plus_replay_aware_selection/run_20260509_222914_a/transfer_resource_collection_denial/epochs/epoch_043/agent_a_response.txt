def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    reslist = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h:
                reslist.append((rx, ry))

    if not reslist:
        return [0, 0]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def manh(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    best_target = reslist[0]
    best_score = -10**18
    for rx, ry in reslist:
        sd = manh(x, y, rx, ry)
        od = manh(ox, oy, rx, ry)
        s = od - sd  # advantage over opponent toward that resource
        if s > best_score:
            best_score = s
            best_target = (rx, ry)
        elif s == best_score:
            if sd < manh(x, y, best_target[0], best_target[1]):
                best_target = (rx, ry)

    tx, ty = best_target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = 10**18
    best_adv = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        sd = manh(nx, ny, tx, ty)
        od = manh(ox, oy, tx, ty)
        adv = od - sd
        if sd < best_val or (sd == best_val and adv > best_adv):
            best_val = sd
            best_adv = adv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]