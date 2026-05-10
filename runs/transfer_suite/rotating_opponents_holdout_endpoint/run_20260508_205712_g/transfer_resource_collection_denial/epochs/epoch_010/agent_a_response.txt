def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)
    best_t = None
    best_key = None
    for r in resources:
        if r in obstacles:
            continue
        sd = man(my, r)
        od = man(opp, r)
        key = (od - sd, -sd, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best_t = r
    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nds = man((nx, ny), (tx, ty))
        ndo = man(opp, (tx, ty))
        res_bonus = 1 if (nx, ny) == (tx, ty) else 0
        opp_pressure = man((nx, ny), (ox, oy))
        cand.append(((ndo - nds), res_bonus, -nds, -opp_pressure, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    _, _, _, _, dx, dy = cand[0]
    return [dx, dy]