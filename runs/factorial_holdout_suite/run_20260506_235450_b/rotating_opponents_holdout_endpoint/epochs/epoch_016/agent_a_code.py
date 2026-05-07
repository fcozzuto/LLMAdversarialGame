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

    def parse_xy(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict) and "x" in r and "y" in r:
            return int(r["x"]), int(r["y"])
        return None

    best = None
    best_key = None
    for r in resources:
        p = parse_xy(r)
        if not p:
            continue
        rx, ry = p
        if sx == rx and sy == ry:
            return [0, 0]
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (do - ds, -ds, -abs(rx - sx), -abs(ry - sy))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No resources visible: move away from opponent along a valid diagonal/step
        deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        bestd = None
        bestk = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_opp = man(nx, ny, ox, oy)
            k = (d_opp, -(abs(dx) + abs(dy)))
            if bestk is None or k > bestk:
                bestk = k
                bestd = (dx, dy)
        return [bestd[0], bestd[1]] if bestd else [0, 0]

    tx, ty = best
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic preference order for ties:
    # prefer moves that reduce our distance most; then keep opponent distance large; then prefer diagonals earlier.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        # Approximate "will opponent beat me to next" by comparing our ds2 to our previous ds:
        # Also reward keeping opponent far from the target.
        # Since opponent doesn't move, do2 is constant, but keep term for future robustness if observation changes.
        score = (-(ds2), do2, -(abs(dx) + abs(dy)), -0 if (dx == 0 and dy == 0) else 1)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]