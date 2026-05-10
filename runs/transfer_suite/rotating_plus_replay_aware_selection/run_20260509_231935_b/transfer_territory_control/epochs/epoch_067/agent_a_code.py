def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = observation.get("obstacles") or []
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            targets.append((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    if not targets:
        for p in unclaimed:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                targets.append((int(p[0]), int(p[1])))

    if not targets:
        targets = [(ox, oy)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        dmin = min(man(nx, ny, tx, ty) for tx, ty in targets)
        do = man(nx, ny, ox, oy)
        if targets and targets[0] == (ox, oy) and len(targets) == 1:
            val = do  # no known targets: move away from opponent
        else:
            val = -dmin * 10 + do  # approach targets, keep distance from opponent
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]