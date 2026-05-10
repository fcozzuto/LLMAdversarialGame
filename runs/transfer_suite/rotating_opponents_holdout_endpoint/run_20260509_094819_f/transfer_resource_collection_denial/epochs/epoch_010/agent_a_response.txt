def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_target = None
    best_key = None
    if resources:
        for r in resources:
            if not isinstance(r, (list, tuple)) or len(r) < 2:
                continue
            tx, ty = int(r[0]), int(r[1])
            if not valid(tx, ty) or (tx, ty) == (sx, sy):
                # if we are already on it, movement will be [0,0] by move choice below
                pass
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            # Prefer targets we can reach earlier (maximize do-ds), then closer, then deterministic
            key = (-(do - ds), ds, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best_target = (tx, ty)

    tx, ty = (w // 2, h // 2) if best_target is None else best_target

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(nx, ny, ox, oy)
        # Primary: minimize distance to target; Secondary: keep away from opponent; Tertiary deterministic by move
        cand.append(((ds2, -do2, dx, dy), [dx, dy]))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda z: z[0])
    return cand[0][1]