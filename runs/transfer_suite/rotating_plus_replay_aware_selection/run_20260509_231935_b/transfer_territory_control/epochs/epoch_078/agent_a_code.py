def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    unclaimed = observation.get("unclaimed_cells") or []
    unq = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2)

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    st = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) == 2)
    ot = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) == 2)

    cx = (w - 1) // 2
    cy = (h - 1) // 2

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0
        sc = 0.0
        if (nx, ny) in ot:
            sc += 18.0
        elif (nx, ny) in unq:
            sc += 10.0
        elif (nx, ny) in st:
            sc += 6.0
        else:
            sc += 4.0

        dsc = man(nx, ny, cx, cy)
        sc += -0.7 * dsc
        sc += 0.35 * man(ox, oy, cx, cy)  # discourage letting opponent keep center

        dso = man(nx, ny, ox, oy)
        sc += -0.08 * dso  # slight pressure toward opponent

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [int(dx), int(dy)]
    return best