def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for o in obstacles:
        try:
            x, y = o
            obs_set.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        key = (-(adv), ds, ry, rx)  # minimize -adv => maximize adv; then closer; then stable tie
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        ds1 = man(nx, ny, rx, ry)
        do1 = man(ox, oy, rx, ry)
        adv1 = do1 - ds1
        # Prefer moves that increase our advantage; then reduce our distance; then stable direction preference
        mkey = (-(adv1), ds1, dy, dx)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]