def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c is not None and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c is not None and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c is not None and len(c) >= 2)

    resources = []
    for r in (observation.get("resources") or []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y) and (x, y) != (ox, oy):
                resources.append((x, y))

    dirs = [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        cell = (nx, ny)
        score = 0
        if cell in self_t:
            score += 2
        if cell in unclaimed:
            score += 10
        if cell in opp_t:
            score += 22  # encourage flipping into enemy-controlled cells

        if resources:
            dres = abs(nx - resources[0][0]) + abs(ny - resources[0][1])
            for (rx, ry) in resources[1:]:
                d = abs(nx - rx) + abs(ny - ry)
                if d < dres: dres = d
            score += max(0, 7 - dres)
        else:
            # drive toward nearest unclaimed if no resources visible
            if unclaimed:
                dun = None
                for (ux, uy) in unclaimed:
                    if free(ux, uy):
                        d = abs(nx - ux) + abs(ny - uy)
                        if dun is None or d < dun:
                            dun = d
                if dun is not None:
                    score += max(0, 6 - dun)

        # reduce chance of feeding the opponent sweeper: avoid entering cells close to opponent territory boundary
        if opp_t:
            mind = None
            for (tx, ty) in opp_t:
                d = abs(nx - tx) + abs(ny - ty)
                if mind is None or d < mind:
                    mind = d
            if mind is not None:
                score -= 4 * max(0, 3 - mind)

        # mild preference to increase distance from opponent position unless we are flipping it
        dnow = abs(sx - ox) + abs(sy - oy)
        dnew = abs(nx - ox) + abs(ny - oy)
        if cell not in opp_t:
            score += 0.5 * (dnew - dnow)

        if score > best[1]:
            best = ([dx, dy], score)
    return best[0] if best[0] is not None else [0, 0]