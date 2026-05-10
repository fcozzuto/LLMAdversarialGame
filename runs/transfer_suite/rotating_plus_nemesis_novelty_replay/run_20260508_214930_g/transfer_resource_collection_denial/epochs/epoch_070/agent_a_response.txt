def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            best_adv = -10**9
            best_self_d = 10**9
            best_cell = None
            for tx, ty in resources:
                sd = cheb(nx, ny, tx, ty)
                od = cheb(ox, oy, tx, ty)
                adv = od - sd
                if adv > best_adv or (adv == best_adv and (sd < best_self_d or (sd == best_self_d and (tx, ty) < best_cell))):
                    best_adv = adv
                    best_self_d = sd
                    best_cell = (tx, ty)
            # Prefer positive race advantage; if none, still go toward closest resource.
            cand.append((best_adv, -best_self_d, dx, dy))

    if not cand:
        return [0, 0]

    # Deterministic tie-break: lexicographic by (best_adv, -best_self_d, dx, dy)
    cand.sort(reverse=True)
    return [cand[0][2], cand[0][3]]