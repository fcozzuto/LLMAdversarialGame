def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        best_key = None
        for r in resources:
            ds = dist((sx, sy), r)
            do = dist((ox, oy), r)
            # Prefer resources where we are closer (do - ds is larger).
            key = (do - ds, -ds, r[0], r[1])
            if best_key is None or key > best_key:
                best_key = key
                best = r
        tx, ty = best
    else:
        # No resources visible: head toward center-ish deterministically.
        tx, ty = w // 2, h // 2

    def score_move(dx, dy):
        ns = (sx + dx, sy + dy)
        no = (ox + 0, oy + 0)
        ds = dist(ns, (tx, ty))
        do = dist(no, (tx, ty))
        adv = do - ds
        # Also avoid edging into positions with more local blockage (simple stability).
        neigh_free = 0
        for ddx, ddy in deltas:
            nx, ny = ns[0] + ddx, ns[1] + ddy
            if inb(nx, ny) and (nx, ny) not in obst:
                neigh_free += 1
        return (adv, -ds, neigh_free, -abs(ns[0] - tx) - abs(ns[1] - ty), dx, dy)

    best_move = None
    best_key = None
    for dx, dy in legal:
        k = score_move(dx, dy)
        if best_key is None or k > best_key:
            best_key = k
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]