def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    valid = []
    for p in resources:
        if not p or len(p) < 2:
            continue
        rx, ry = int(p[0]), int(p[1])
        if inb(rx, ry) and (rx, ry) not in obs:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    scored = []
    for rx, ry in valid:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        adv = opd - myd
        # Prefer resources where we can arrive no later; otherwise still keep targets with large opponent disadvantage.
        if myd <= opd:
            sc = 200000 + adv * 2000 - myd * 3
        else:
            sc = 50000 + adv * 800 - myd * 5
        # Small deterministic tie-break by coordinates
        sc = sc - rx * 0.01 - ry * 0.001
        scored.append((sc, rx, ry))
    scored.sort(reverse=True)
    top = scored[:min(6, len(scored))]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Evaluate move by best achievable advantage on top targets.
        move_sc = -10**18
        for _, rx, ry in top:
            myd2 = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            adv2 = opd - myd2
            if myd2 <= opd:
                sc2 = 150000 + adv2 * 2500 - myd2 * 4
            else:
                sc2 = 30000 + adv2 * 1000 - myd2 * 6
            # Slightly prefer progress toward nearer target
            sc2 = sc2 - (rx - nx) * 0.0001 - (ry - ny) * 0.0001
            if sc2 > move_sc:
                move_sc = sc2
        if best_score is None or move_sc > best_score:
            best_score = move_sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]