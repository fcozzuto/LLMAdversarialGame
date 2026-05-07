def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))
        elif isinstance(a, dict) and "x" in a and "y" in a:
            obs.add((int(a["x"]), int(a["y"])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target deterministically: maximize advantage (opp farther - self nearer),
    # with a secondary preference for closer self.
    best = None
    best_key = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            rx, ry = int(r["x"]), int(r["y"])
        else:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if ds == 0:
            return [0, 0]
        key = (do - ds, -ds)  # larger advantage, then closer
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]

    rx, ry = best
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves.sort(key=lambda t: (0 if (t[0] == 0 and t[1] == 0) else 1, t[0], t[1]))

    best_move = (0, 0)
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = man(nx, ny, rx, ry)
        no = man(ox, oy, rx, ry)  # opponent doesn't move this turn
        adv = no - ns
        # Prefer reaching target faster; tiebreak by maximizing advantage and staying safe.
        eval_key = (adv, -ns, -man(nx, ny, ox, oy))
        if best_eval is None or eval_key > best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]