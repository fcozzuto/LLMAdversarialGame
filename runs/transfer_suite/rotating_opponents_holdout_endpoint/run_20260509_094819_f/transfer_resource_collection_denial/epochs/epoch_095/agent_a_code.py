def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Choose a target resource where we are relatively closest vs opponent
    if resources:
        best = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            rel = sd - od
            # Prefer negative rel (we likely arrive first); then minimize sd; then tie-break by lexicographic target
            key = (rel, sd, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        tx, ty = best[1]
        best_move = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            nd = cheb(nx, ny, tx, ty)
            # Also prevent walking into moves that worsen relative access too much
            nod = cheb(ox, oy, tx, ty)
            rel2 = nd - nod
            key = (abs(rel2), nd, abs(ox - nx) + abs(oy - ny), nx, ny)
            if key < best_move:
                best_move = key
                ret = [dx, dy]
        return ret if best_move[0] != 10**9 else [0, 0]

    # If no resources, deterministically move to a "sweep line" advantage: closest free cell to opponent row/col
    target_x, target_y = ox, oy
    best = None
    ret = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d = abs(nx - target_x) + abs(ny - target_y)
        key = (d, nx, ny)
        if best is None or key < best:
            best = key
            ret = [dx, dy]
    return ret