def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            pos = r.get("pos")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            else:
                x = r.get("x")
                y = r.get("y")
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def best_resource():
        best = None
        bestv = -10**9
        for x, y in resources:
            if not inb(x, y):
                continue
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            # Prefer resources we can reach quickly, and that are relatively safer from opponent.
            v = (do - ds) * 10 - ds
            # Slightly favor resources nearer to our corner to avoid over-rotating across the map.
            v += -cheb(sx, sy, 0, 0) * 0.1
            # Deterministic tie-break.
            if v > bestv or (v == bestv and (x, y) < best):
                bestv = v
                best = (x, y)
        return best

    target = best_resource()

    if target is None:
        # No valid resource: drift toward center-ish but away from opponent for tempo control.
        candidates = []
        for dx, dy in ((0, -1), (1, 0), (0, 0), (-1, 0), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                # maximize distance from opponent, then prefer toward board center
                v = cheb(nx, ny, ox, oy) * 5 - cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
                candidates.append((v, dx, dy))
        candidates.sort(reverse=True)
        return [int(candidates[0][1]), int(candidates[0][2])] if candidates else [0, 0]

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Greedy toward target with opponent-aware safety.
        v = -cheb(nx, ny, tx, ty) * 10 + cheb(nx, ny, ox, oy)
        # Prefer staying still if equally good to prevent oscillations near obstacles.
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]