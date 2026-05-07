def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If already on a resource, prefer staying.
    for rx, ry in resources:
        if (rx, ry) not in obst and rx == sx and ry == sy:
            return [0, 0]

    best = (0, 0)
    best_val = -10**18

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        val = 0
        # Prefer moves that win more resources (arrive earlier than opponent).
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ourd = cheb(nsx, nsy, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            if ourd == 0:
                val += 10**6
            elif ourd < oppd:
                val += (oppd - ourd + 1) * 50
            elif ourd == oppd:
                val += 10
            else:
                val -= (ourd - oppd + 1) * 20

        # Anti-deny: if opponent is much closer to some resource, bias toward reducing our distance there.
        if resources:
            worst_target = None
            worst_opp = -1
            for rx, ry in resources:
                if (rx, ry) in obst:
                    continue
                oppd = cheb(ox, oy, rx, ry)
                if oppd > worst_opp:
                    worst_opp = oppd
                    worst_target = (rx, ry)
            if worst_target is not None:
                rx, ry = worst_target
                val -= cheb(nsx, nsy, rx, ry) * 2

        # Slightly prefer increasing distance from opponent when competitive.
        val += (cheb(nsx, nsy, ox, oy) - cheb(sx, sy, ox, oy))

        if val > best_val:
            best_val = val
            best = (mdx, mdy)

    return [int(best[0]), int(best[1])]