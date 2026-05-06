def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def d(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_pos = None
    best_adv = -10**9
    any_valid = False
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        any_valid = True
        sd = d(sx, sy, rx, ry)
        od = d(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer
        if adv > best_adv or (adv == best_adv and sd < (best_pos[0] if best_pos else 10**9)):
            best_adv = adv
            best_pos = (sd, rx, ry)
    if not any_valid:
        return [0, 0]

    target_sd, tx, ty = best_pos
    pos_is_adv = best_adv > 0

    def neighbor_penalty(x, y):
        # mild penalty for moving adjacent to obstacles (avoid congestion)
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in blocked:
                    pen += 1
        return pen

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nds = d(nx, ny, tx, ty)
        ndo = d(ox, oy, tx, ty)
        cur = d(sx, sy, tx, ty)
        prog = cur - nds  # prefer progress
        # If we don't have a closer-to-target advantage, shift to absolute progress toward closest resource.
        if pos_is_adv:
            key = (nds - ndo, -prog, neighbor_penalty(nx, ny), tx, ty)
        else:
            # closest-resource mode: minimize nds, then deny opponent by increasing their distance to our eventual best.
            best_opp_dist = 10**9
            for rx, ry in resources:
                if not inb(rx, ry):
                    continue
                best_opp_dist = min(best_opp_dist, d(ox, oy, rx, ry))
            key = (nds, neighbor_penalty(nx, ny), -best_opp_dist, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]