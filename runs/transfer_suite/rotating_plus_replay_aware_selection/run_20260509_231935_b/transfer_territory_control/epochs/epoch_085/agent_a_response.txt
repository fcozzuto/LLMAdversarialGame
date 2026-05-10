def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2)

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_terr if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) == 2)

    # Centroid for stability (deterministic; small rounding)
    n = len(self_set)
    if n:
        cx = sum(x for x, _ in self_set) // n
        cy = sum(y for _, y in self_set) // n
    else:
        cx, cy = sx, sy

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    # Find a couple closest unclaimed cells (for guidance)
    # Keep it cheap/deterministic by sampling first few list entries.
    closest = None
    for i, p in enumerate(unclaimed[:12]):
        if not (isinstance(p, (list, tuple)) and len(p) == 2):
            continue
        x, y = int(p[0]), int(p[1])
        if not inside(x, y) or (x, y) in obs:
            continue
        d = man(sx, sy, x, y)
        if closest is None or d < closest[0]:
            closest = (d, x, y)

    best = None
    best_move = [0, 0]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            sc = -10  # discourage obstacle hits / invalid moves
        else:
            sc = 0
            if (nx, ny) in self_set:
                sc += 1.0
            elif (nx, ny) in un_set:
                sc += 3.5  # prioritize claiming unclaimed territory
            elif (nx, ny) in opp_set:
                sc -= 2.0  # don't blindly dive into opponent territory

            # Prefer staying cohesive and pushing away from opponent
            sc += -0.05 * man(nx, ny, cx, cy)
            sc += 0.05 * man(nx, ny, ox, oy)

            # If we have unclaimed targets, reduce distance to them
            if closest is not None:
                sc += -0.08 * man(nx, ny, closest[1], closest[2])

            # Slight edge pressure for longer-term control
            if nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1:
                sc += -0.2
        if best is None or sc > best:
            best = sc
            best_move = [dx, dy]
    return best_move