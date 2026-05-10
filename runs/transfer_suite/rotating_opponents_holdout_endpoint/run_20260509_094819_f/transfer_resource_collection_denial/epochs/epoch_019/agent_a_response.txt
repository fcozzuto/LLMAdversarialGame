def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    valid = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry):
                ds = man(sx, sy, rx, ry)
                do = man(ox, oy, rx, ry)
                # Prefer resources where we are closer; otherwise choose least-losing contest.
                adv = do - ds
                valid.append((adv, -ds, rx, ry, ds, do))

    if not valid:
        return [0, 0]

    best = None
    for item in valid:
        adv, negds, rx, ry, ds, do = item
        key = (1 if adv > 0 else 0, adv, negds)  # deterministic priority
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_to_o = man(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: also reduce distance to opponent slightly (interception).
        cand = (d_to_t, d_to_o, dx, dy)
        if cand < best_move[:4]:
            best_move = cand + (dx, dy)
    return [best_move[4], best_move[5]]