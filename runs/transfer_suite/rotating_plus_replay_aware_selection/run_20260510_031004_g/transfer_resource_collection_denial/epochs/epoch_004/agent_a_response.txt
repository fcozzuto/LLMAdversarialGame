def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target: prefer resources we can reach earlier; tie-break with distance and spread from opponent.
    best_t = None
    best_key = None
    for r in resources:
        tx, ty = int(r[0]), int(r[1])
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        key = (od - sd, -sd, -od, -abs(tx - ox) - abs(ty - oy), tx, ty)
        if best_key is None or key > best_key:
            best_key, best_t = key, (tx, ty)

    tx, ty = best_t

    # Local move: minimize our remaining distance; maximize reach advantage; avoid obstacles tightly.
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Encourage safety margin around obstacles (penalize stepping adjacent to obstacles).
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj += 1
        # Also prefer not to move away from target even if obstacle-avoidance is same.
        key = (-(myd), (opd - myd), -(adj), -abs(nx - ox) - abs(ny - oy), tx - nx, ty - ny)
        cand.append((key, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort(reverse=True)
    _, dx, dy = cand[0]
    return [int(dx), int(dy)]