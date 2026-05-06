def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))
    if not targets:
        return [0, 0]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Choose a target where we can beat the opponent or where we are closest relative to them.
        best_val_for_move = -10**18
        for tx, ty in targets:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            if sd == 0:
                val = 10**9 - od * 10
            else:
                # Prefer winning races; also prefer reducing opponent's lead if race is lost.
                race = od - sd  # positive means we arrive first (or sooner)
                val = race * 1000 - sd * 5 + (1 if (tx + ty) % 2 == 0 else 0)
            if val > best_val_for_move:
                best_val_for_move = val
        if best is None or best_val_for_move > best[0]:
            best = (best_val_for_move, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]