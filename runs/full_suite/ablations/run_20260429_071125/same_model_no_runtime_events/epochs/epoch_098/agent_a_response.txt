def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    rem = int(observation.get("remaining_resource_count") or len(resources))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if resources:
            # Steal: prioritize resources where we gain closeness over the opponent.
            best_adv = -10**9
            best_d = 10**9
            for tx, ty in resources:
                myd = cheb(nx, ny, tx, ty)
                opd = cheb(ox, oy, tx, ty)
                adv = opd - myd  # higher means we are closer
                # Secondary tie-break: closer to the chosen resource
                if adv > best_adv or (adv == best_adv and myd < best_d):
                    best_adv = adv
                    best_d = myd

            # Late game: if little remains, also reduce opponent threat to any remaining resource.
            if rem <= 3:
                worst_opp = -10**9
                for tx, ty in resources:
                    opd = cheb(ox, oy, tx, ty)
                    if opd > worst_opp:
                        worst_opp = opd
                # Encourage pushing into mid-zone rather than mirroring the opponent.
                threat_pen = (cheb(nx, ny, ox, oy) == 0) * 0
            else:
                threat_pen = 0

            val = (best_adv * 1000) - best_d - threat_pen
        else:
            # No visible resources: move to center, then away from opponent slightly.
            cx, cy = w // 2, h // 2
            myd = cheb(nx, ny, cx, cy)
            oppd = cheb(nx, ny, ox, oy)
            val = (oppd * 2) - myd

        if best is None or val > best[0]:
            best = (val, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]