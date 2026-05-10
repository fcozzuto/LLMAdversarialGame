def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    opp_list = list(opp) if opp else []
    un_list = list(unclaimed) if unclaimed else []

    def mindist(nx, ny, pts):
        if not pts:
            return 10**9
        dmin = 10**9
        for px, py in pts:
            d = abs(px - nx) + abs(py - ny)
            if d < dmin:
                dmin = d
        return dmin

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        sc = 0
        if (nx, ny) in opp:
            sc += 500
        if (nx, ny) in selft:
            sc += 30
        if (nx, ny) in unclaimed:
            sc += 120

        d0 = mindist(x, y, opp_list) if opp_list else 10**9
        d1 = mindist(nx, ny, opp_list) if opp_list else 10**9
        sc += (d0 - d1) * 8

        u0 = mindist(x, y, un_list) if un_list else 10**9
        u1 = mindist(nx, ny, un_list) if un_list else 10**9
        sc += (u0 - u1) * 3

        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]