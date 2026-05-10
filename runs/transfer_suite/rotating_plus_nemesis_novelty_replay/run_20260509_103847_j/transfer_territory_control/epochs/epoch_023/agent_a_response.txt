def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer counter-claim progress: take unclaimed, then opponent cells (flip).
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        s = 0
        if (nx, ny) in unT:
            s += 5
        elif (nx, ny) in opT:
            s += 8
        elif (nx, ny) in selfT:
            s += 1
        else:
            s += 0  # unknown but not in provided sets

        # Pressure: reduce distance to opponent; also slightly avoid getting too close without progress.
        d_now = man(sx, sy, ox, oy)
        d_new = man(nx, ny, ox, oy)
        s += 1.5 * (d_now - d_new)

        # Frontier bias: encourage moving toward the boundary of our territory.
        frontier = False
        if (sx, sy) in selfT:
            for ax, ay in dirs:
                tx, ty = sx + ax, sy + ay
                if inb(tx, ty) and (tx, ty) not in selfT and (tx, ty) not in obs:
                    frontier = True
                    break
        if frontier and ((nx, ny) not in selfT):
            s += 2
        if frontier and ((nx, ny) in selfT):
            s -= 1

        # Deterministic tie-breaker: lexicographic on move.
        if s > best_score or (s == best_score and (dx, dy) < best):
            best_score = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]