def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def block_pen(nx, ny):
        # slight penalty for moving "tight" to obstacles
        p = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if (tx, ty) in obstacles:
                    p += 1
        return p

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            self_d = man(nx, ny, tx, ty)
            opp_d = man(nx, ny, ox, oy)
            key = (self_d, -opp_d, block_pen(nx, ny), dx, dy)
            if best is None or key < best:
                best = key
                bd = (dx, dy)
        return [bd[0], bd[1]]

    best_key = None
    best_move = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        b_self = 10**9
        b_adv = -10**9
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # prefer resources we can make progress toward while keeping an advantage
            adv = (d_opp - d_self)
            if d_self < b_self or (d_self == b_self and adv > b_adv):
                b_self, b_adv = d_self, adv
        # primary: approach; secondary: advantage; tertiary: avoid obstacles; deterministic tie-break
        key = (b_self, -b_adv, block_pen(nx, ny), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]