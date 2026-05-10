def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles", []) or []
    obst = set((int(x), int(y)) for x, y in obs)

    resources = observation.get("resources", []) or []
    res = [(int(x), int(y)) for x, y in resources]

    unclaimed = observation.get("unclaimed_cells", []) or []
    uc = set((int(x), int(y)) for x, y in unclaimed)

    s_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    o_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obst

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (10**9, 0, (0, 0))

    # Prefer expanding to unclaimed adjacent to our territory; otherwise near resources; otherwise toward center.
    targets = []
    if s_terr and uc:
        for x, y in s_terr:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                t = (x + dx, y + dy)
                if t in uc:
                    targets.append(t)
    if not targets and res:
        targets = res
    if not targets:
        targets = [(w // 2, h // 2)]

    # If opponent is close, slightly bias away.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Distance to best target
        md = 10**9
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if d < md:
                md = d
        # Penalty for moving near opponent territory/cell if available
        opp_pen = 0
        if o_terr:
            for px, py in o_terr:
                d2 = abs(nx - px) + abs(ny - py)
                if d2 <= 2:
                    opp_pen += (3 - d2)
        d_op = abs(nx - ox) + abs(ny - oy)
        opp_pen += (0 if d_op >= 4 else (4 - d_op))

        # Prefer smaller md, then smaller opp_pen, then deterministic tie-break on dx,dy
        key = (md, opp_pen, dx, dy)
        if key < best:
            best = key

    return [best[2], best[3]]