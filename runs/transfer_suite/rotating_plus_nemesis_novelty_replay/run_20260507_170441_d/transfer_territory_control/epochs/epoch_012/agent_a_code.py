def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                blocked.add((x, y))
        except:
            pass

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    candidates = []
    for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    # If unclaimed exists: chase nearest. Else: expand toward center.
    if unclaimed:
        tlist = []
        for p in unclaimed:
            try:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in blocked:
                    tlist.append((x, y))
            except:
                pass
    else:
        tlist = []

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    opp_adj = set()
    for (x, y) in opp_terr:
        for ddx, ddy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            ax, ay = x + ddx, y + ddy
            if inb(ax, ay) and (ax, ay) not in blocked:
                opp_adj.add((ax, ay))

    best = None
    bestv = -10**18
    for dx, dy, nx, ny in candidates:
        if (nx, ny) in opp_terr:
            base = 1.5e6  # strongly prefer capturing opponent control
        else:
            base = 0.0
        adj_bonus = 1200.0 if (nx, ny) in opp_adj else 0.0

        if tlist:
            # nearest unclaimed distance
            dmin = 10**18
            for tx, ty in tlist:
                dd = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
                if dd < dmin:
                    dmin = dd
            chase = -dmin
        else:
            chase = -dist2((nx, ny), (cx, cy)) * 1000.0

        # mild preference to move toward opponent when unclaimed is empty; otherwise keep to expansion
        opp_press = -dist2((nx, ny), (ox, oy)) * (0.2 if not tlist else 0.02)

        v = base + adj_bonus + chase + opp_press
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]