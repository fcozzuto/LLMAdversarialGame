def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if inb(tx, ty) and (tx, ty) not in obs:
                sd = cheb(sx, sy, tx, ty)
                od = cheb(ox, oy, tx, ty)
                lead = od - sd  # bigger is better
                close_enemy_pen = 2 if cheb(ox, oy, tx, ty) <= 1 else 0
                key = (lead - close_enemy_pen, -sd, tx, ty)
                candidates.append((key, (tx, ty)))
    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    tx, ty = candidates[0][1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        move_lead = nod - nsd
        cell_pen = 0
        if cheb(nx, ny, ox, oy) == 0:
            cell_pen += 100  # avoid accidental collision-like overlap
        if cheb(nx, ny, ox, oy) == 1:
            cell_pen += 1  # slightly avoid giving denial advantage
        score = (move_lead - cell_pen, -nsd, nx, ny)
        if best is None or score > best[0]:
            best = (score, (dx, dy))
    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]