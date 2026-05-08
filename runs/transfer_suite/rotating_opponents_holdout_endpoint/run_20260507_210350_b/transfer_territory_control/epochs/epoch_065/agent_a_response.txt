def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a deterministic global target: prefer nearest opponent cell, then nearest unclaimed; else chase opponent.
    opp_list = list(oppT)
    un_list = list(unclaimed)
    if opp_list:
        tx, ty = min(opp_list, key=lambda c: (cheb((sx, sy), c), c[0], c[1]))
    elif un_list:
        tx, ty = min(un_list, key=lambda c: (cheb((sx, sy), c), c[0], c[1]))
    else:
        tx, ty = ox, oy

    best = [0, 0, -10**9]  # dx, dy, score
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        tgt = (nx, ny)
        if tgt in oppT:
            claim = 3.0
        elif tgt in unclaimed:
            claim = 2.0
        elif tgt in selfT:
            claim = 0.2
        else:
            claim = 0.0

        dist = cheb((nx, ny), (tx, ty))
        # Prefer approaching target; also avoid getting adjacent too far from opponent's bulk when we're far.
        opp_dist = cheb((nx, ny), (ox, oy))
        score = claim * 10 - dist - 0.05 * opp_dist

        # Deterministic tie-break: lowest dx, then lowest dy.
        if score > best[2] or (score == best[2] and (dx < best[0] or (dx == best[0] and dy < best[1]))):
            best = [dx, dy, score]

    return [int(best[0]), int(best[1])]