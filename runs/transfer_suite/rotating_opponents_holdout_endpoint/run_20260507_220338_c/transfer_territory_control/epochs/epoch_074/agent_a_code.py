def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    def min_dist_to_set(x, y, S):
        if not S:
            return 999
        md = 999
        for a, b in S:
            dx = x - a
            dy = y - b
            d = dx * dx + dy * dy
            if d < md:
                md = d
        return md

    # Prefer moves that (a) grab unclaimed, (b) enter opponent territory to flip, (c) reduce distance to opponent territory.
    best_move = [0, 0]
    best_val = -10**18

    # Mild center/edge bias: avoid corners unless near (good vs center-claim archetype).
    corner_pen = 0
    if (sx in (0, w - 1)) and (sy in (0, h - 1)):
        corner_pen = -5

    opp_dist = min_dist_to_set(sx, sy, opp_terr)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        val = 0
        if (nx, ny) in opp_terr:
            val += 260
        elif (nx, ny) in unclaimed:
            val += 65
        elif (nx, ny) in self_terr:
            val += 8

        # Progress to opponent territory boundary
        nd = min_dist_to_set(nx, ny, opp_terr)
        if nd < 999:
            val += (opp_dist - nd) * 1.8

        # Avoid walking into the closest unclaimed "dead" area: reward openness by counting free neighbors
        free = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if ok(ax, ay):
                free += 1
        val += free * 0.6

        # Corner penalty (except if it's also opponent/unclaimed)
        if (nx in (0, w - 1)) and (ny in (0, h - 1)):
            if (nx, ny) not in opp_terr:
                val -= 10

        # Tie-breaker deterministically toward smaller dx,dy ordering by fixed dir list position
        val += corner_pen

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move