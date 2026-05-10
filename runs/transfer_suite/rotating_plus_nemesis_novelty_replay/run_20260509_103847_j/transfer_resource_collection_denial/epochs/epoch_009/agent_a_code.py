def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    opp = (ox, oy)
    best_r = None
    best_key = None
    for r in resources:
        sd = man((sx, sy), r)
        od = man(opp, r)
        adv = od - sd  # positive => we are closer
        key = (-adv, sd > od, sd, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man((nx, ny), (tx, ty))
        od2 = man(opp, (tx, ty))
        adv2 = od2 - sd2
        # Prefer maximizing our advantage; if tie, get closer to target; avoid moves that worsen relative distance to opponent overall.
        self_to_opp = man((nx, ny), opp)
        key = (-adv2, sd2, self_to_opp, tx == nx and ty == ny, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]