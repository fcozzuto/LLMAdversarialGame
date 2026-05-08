def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    best_targets = []
    for tx, ty in res:
        sd = man(sx, sy, tx, ty)
        td = man(ox, oy, tx, ty)
        # Prefer resources where we're not behind; also favor closer targets.
        key = (td - sd, -sd, -(abs(tx + ty)))
        best_targets.append((key, (tx, ty)))
    best_targets.sort(key=lambda z: z[0], reverse=True)
    candidates = [best_targets[i][1] for i in range(min(4, len(best_targets)))]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Look one step ahead toward the best reachable target.
        mk = None
        for tx, ty in candidates:
            sd2 = man(nx, ny, tx, ty)
            # discourage moving into squares that let opponent instantly get a top target
            # (resource_denier style), by measuring opponent relative progress.
            td = man(ox, oy, tx, ty)
            key = (td - sd2, -sd2, -abs(tx - nx) - abs(ty - ny), -tx)
            if mk is None or key > mk:
                mk = key
        if mk is None:
            continue
        if best_key is None or mk > best_key:
            best_key = mk
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]