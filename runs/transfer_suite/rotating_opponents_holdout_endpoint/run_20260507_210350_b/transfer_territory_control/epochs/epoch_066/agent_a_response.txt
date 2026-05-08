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

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        d1 = ax - bx
        if d1 < 0: d1 = -d1
        d2 = ay - by
        if d2 < 0: d2 = -d2
        return d1 if d1 >= d2 else d2

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_count = int(observation.get("self_territory_count") or len(selfT))
    opp_count = int(observation.get("opponent_territory_count") or len(oppT))

    # Targeting: if behind, attack opponent territory; if ahead, claim unclaimed; tie -> opportunistically attack.
    if opp_count > self_count:
        candidates = list(oppT) if oppT else list(unclaimed)
    elif self_count > opp_count:
        candidates = list(unclaimed) if unclaimed else list(oppT)
    else:
        candidates = (list(oppT) + list(unclaimed)) if (oppT or unclaimed) else [tuple(op)]

    if not candidates:
        tx, ty = ox, oy
    else:
        tx, ty = min(candidates, key=lambda c: (cheb((sx, sy), c), c[0], c[1]))

    # Evaluate one-step moves greedily with deterministic tie-breaking.
    best = (10**9, 10**9, 10**9, 0, 0)  # (score, dist, danger, dx, dy)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue

            d = cheb((nx, ny), (tx, ty))
            nxt = (nx, ny)

            # Prefer moves that enter/press into opponent territory.
            danger = 0
            if nxt in oppT:
                danger -= 2
            elif nxt in selfT:
                danger += 1
            elif nxt in unclaimed:
                danger -= 1

            # Extra: slightly discourage moving closer to opponent if we're not attacking target.
            # (keeps deterministic defense while claiming)
            if (tx, ty) not in oppT:
                # only if still near opponent territory
                if cheb((nx, ny), (ox, oy)) < cheb((sx, sy), (ox, oy)):
                    danger += 1

            score = d + (danger * 0.1) + (0.01 * (nx - sx) * (nx - sx + 1))
            cand = (score, d, danger, dx, dy)
            if cand < best:
                best = cand

    # If all moves blocked, stay.
    return [int(best[3]), int(best[4])]