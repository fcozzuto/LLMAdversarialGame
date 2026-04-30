def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a resource based on who can reach it first (deterministic).
    if resources:
        best_r = None
        best_adv = -10**18
        best_my = 10**18
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            oppd = man(ox, oy, rx, ry)
            adv = oppd - myd  # positive means we are closer (or equal)
            if adv > best_adv or (adv == best_adv and (myd < best_my or (myd == best_my and (rx, ry) < best_r))):
                best_adv = adv
                best_my = myd
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # No visible resources: move toward the opposite corner while avoiding obstacles locally.
        tx, ty = (7, 7) if (sx <= 3 and sy <= 3) else (0, 0)

    # Evaluate candidate moves with a mix of reaching target and denying opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_to_t = man(nx, ny, tx, ty)
        opp_to_t = man(ox, oy, tx, ty)
        # Prefer increasing advantage vs opponent; smaller target distance; slight tie-break toward opponent to block lanes.
        val = 0
        val += (my_to_t == 0) * 100000
        val += (opp_to_t - my_to_t) * 1000
        val += -my_to_t * 10
        val += -((ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)) * 0.001
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]