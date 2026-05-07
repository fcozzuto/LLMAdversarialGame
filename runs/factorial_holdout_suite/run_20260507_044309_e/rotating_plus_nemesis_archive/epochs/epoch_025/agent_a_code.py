def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Target selection: prefer resources where we gain over opponent, but still close.
    # If we're far and opponent much closer, still go but reduced.
    my = (sx, sy)
    op = (ox, oy)
    scored = []
    for t in resources:
        self_d = md(my, t)
        opp_d = md(op, t)
        gain = (opp_d - self_d)
        # prioritize immediate race advantage; tie-break by smaller self_d then coordinates
        scored.append(((-gain * 2) + self_d * 0.5, self_d, t[0], t[1], t))
    scored.sort()
    candidates = [s[4] for s in scored[: min(6, len(scored))]]

    best = (0, 0)
    bestv = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cell = (nx, ny)

        # Evaluate the move by looking at best achievable target from this cell.
        best_pick = None
        for t in candidates:
            sd = md(cell, t)
            od = md(op, t)
            # Race heuristic + slight emphasis on Chebyshev for diagonal approach.
            val = (od - sd) * 10 - sd + cheb(cell, t) * 0.1
            if best_pick is None or val > best_pick:
                best_pick = val
        # Also include immediate proximity if we might step onto a resource.
        # (resources list is small; deterministic tie-break via max over exact eval)
        immediate = 0
        for r in resources:
            if r == cell:
                immediate = 1
                break
        v = best_pick + immediate * 1000
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]