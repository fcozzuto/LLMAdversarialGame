def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best, bestv = (0, 0), -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = cheb(nx, ny, tx, ty) + 0.15 * cheb(nx, ny, ox, oy)
            # deterministic tie-break: prefer lexicographically smaller (dx,dy) via value tweak
            if v < bestv or (v == bestv and (dx, dy) < best):
                pass
        # prefer move that minimizes distance to center but increases distance from opponent
        bestv = 10**18
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = cheb(nx, ny, tx, ty) - 0.2 * cheb(nx, ny, ox, oy)
            if v < bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose a target: maximize (opponent farther than me) while also being reasonably close.
    resources = sorted(resources)
    best_target = resources[0]
    best_tv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # primary: deny opponent (opd - myd), secondary: closeness
        tv = (opd - myd) * 10 - myd + 0.01 * (rx + ry)
        if tv > best_tv:
            best_tv, best_target = tv, (rx, ry)

    rx, ry = best_target
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Encourage reducing my distance; discourage giving opponent advantage.
        val = (opd - myd) * 8 - myd
        # Mild anti-stall: prefer moves that change position unless staying is best.
        if dx != 0 or dy != 0:
            val += 0.15
        # Prefer boundary-correct deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx,