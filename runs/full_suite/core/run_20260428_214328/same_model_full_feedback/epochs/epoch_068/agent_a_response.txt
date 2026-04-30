def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Target selection: prefer resources where we are relatively closer than opponent.
    best_r = resources[0]
    best_val = None
    for (tx, ty) in resources:
        md = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        adv = od - md  # higher is better
        # Penalize chasing resources opponent is closer to; also keep md low.
        val = adv * 10 - md
        if best_val is None or val > best_val or (val == best_val and (md < man(sx, sy, best_r[0], best_r[1]))):
            best_val = val
            best_r = (tx, ty)

    tx, ty = best_r
    best_move = (0, 0)
    best_score = None
    myd0 = man(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        md = man(nx, ny, tx, ty)
        od_next = man(ox, oy, tx, ty)
        # Primary: reduce our distance; Secondary: improve relative advantage; Tertiary: avoid moving away.
        score = (-(md), (od_next - md), -(md - myd0), -(abs(nx - tx) + abs(ny - ty)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]