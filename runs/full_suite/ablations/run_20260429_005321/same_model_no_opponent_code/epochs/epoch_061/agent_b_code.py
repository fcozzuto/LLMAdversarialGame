def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inside(nx, ny) and (nx, ny) not in obstacles

    cands = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if legal(dx, dy):
                cands.append((dx, dy))
    if not cands:
        return [0, 0]

    resources = observation.get("resources", []) or []
    rt = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rt.append((int(r[0]), int(r[1])))
        elif isinstance(r, int):
            x = r % w
            y = r // w
            if inside(x, y):
                rt.append((x, y))

    def dist(ax, ay, bx, by):
        d = ax - bx
        e = ay - by
        if d < 0:
            d = -d
        if e < 0:
            e = -e
        return d + e

    best = cands[0]
    if rt:
        # Prefer moves that improve distance advantage to the best resource.
        bestv = -10**18
        for dx, dy in cands:
            nx, ny = sx + dx, sy + dy
            best_adv = -10**18
            for rx, ry in rt:
                adv = dist(nx, ny, ox, oy) - dist(nx, ny, rx, ry)  # push toward resources, away from opp
                # also consider stealing: opp distance to resource minus our distance
                steal = dist(ox, oy, rx, ry) - dist(nx, ny, rx, ry)
                v = steal * 1000 + adv
                if v > best_adv:
                    best_adv = v
            if best_adv > bestv or (best_adv == bestv and (dx, dy) < best):
                bestv = best_adv
                best = (dx, dy)
    else:
        # No resources: go toward center while keeping distance from opponent.
        cx, cy = w // 2, h // 2
        bestv = -10**18
        for dx, dy in cands:
            nx, ny = sx + dx, sy + dy
            v = (dist(nx, ny, ox, oy) - dist(nx, ny, cx, cy)) * 1000 - dist(nx, ny, cx, cy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)

    return [int(best[0]), int(best[1])]