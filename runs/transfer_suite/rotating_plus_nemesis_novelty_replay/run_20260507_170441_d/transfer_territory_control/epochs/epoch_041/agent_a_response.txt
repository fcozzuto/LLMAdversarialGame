def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (sx, sy) in blocked:
        blocked.discard((sx, sy))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(x, y, a, b):
        return abs(x - a) + abs(y - b)

    # If we're behind, prioritize faster reclamation of unclaimed near our frontier.
    behind = 0
    sc = int(observation.get("self_territory_count", 0) or 0)
    oc = int(observation.get("opponent_territory_count", 0) or 0)
    if sc < oc:
        behind = 1

    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v -= 1500 if behind else 1200
        elif (nx, ny) in self_t:
            v += 80
        if (nx, ny) in unclaimed:
            v += 520 if behind else 420

        d = dist(nx, ny, ox, oy)
        # Avoid being swept: strongly discourage closeness.
        v += 90 - 18 * d

        # Expansion proxy: how many unclaimed cells would we touch next.
        # (Deterministic local frontier building.)
        touch = 0
        for ax, ay in dirs:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in unclaimed:
                touch += 1
        v += 45 * touch

        # If behind, slightly prefer moving toward unclaimed that is far from opponent
        if behind and touch > 0:
            # compute nearest unclaimed distance among neighbors only (cheap)
            nd = 10**9
            for ax, ay in dirs:
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in unclaimed:
                    nd = min(nd, dist(tx, ty, ox, oy))
            if nd < 10**9:
                v += 0.35 * nd

        # Tie-breaker: prefer staying out of opponent if near equal scores
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]