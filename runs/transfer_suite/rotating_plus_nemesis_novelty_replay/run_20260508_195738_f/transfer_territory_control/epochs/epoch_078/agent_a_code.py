def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_list = list(opp)
    un_list = list(unclaimed)

    def nearest_dist(x, y, cells):
        if not cells:
            return 10**9
        md = 10**9
        for cx, cy in cells:
            d = abs(cx - x) + abs(cy - y)
            if d < md:
                md = d
        return md

    if un_list:
        obj_list = un_list
        base = "unclaimed"
    else:
        obj_list = opp_list
        base = "opp"

    d0 = nearest_dist(sx, sy, obj_list)

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        sc = 0
        if (nx, ny) in opp:
            sc += 7
            if base == "unclaimed":
                sc += 2
        elif (nx, ny) in unclaimed:
            sc += 4
        elif (nx, ny) in selft:
            sc += 1

        dn = nearest_dist(nx, ny, obj_list)
        sc += (d0 - dn) * 2

        # Encourage progress toward opponent if no unclaimed
        if base == "opp" and opp_list:
            sc += (d0 - dn)

        # Small tie-breaker: prefer stay less when possible
        if dx == 0 and dy == 0:
            sc -= 0.1

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best