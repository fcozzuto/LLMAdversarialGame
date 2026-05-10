def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(lst):
        s = set()
        for p in (lst or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obs = to_set(observation.get("obstacles", []))
    self_terr = to_set(observation.get("self_territory", []))
    opp_terr = to_set(observation.get("opponent_territory", []))
    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []) if isinstance(p, (list, tuple)) and len(p) >= 2]
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources", []) or []) if isinstance(p, (list, tuple)) and len(p) >= 2]

    targets = resources if resources else unclaimed
    if not targets:
        targets = list(opp_terr) if opp_terr else [(ox, oy)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_val = -10**18
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # deterministic tie-break: fixed order of cand; already deterministic
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d_opp = man(nx, ny, ox, oy)
        if (nx, ny) in opp_terr:
            own_gain = 9.0
        elif (nx, ny) in unclaimed or (nx, ny) not in self_terr:
            own_gain = 3.0
        else:
            own_gain = 1.0

        # prefer moving toward nearest target while keeping distance from opponent
        t_dist = min(man(nx, ny, tx, ty) for (tx, ty) in targets) if targets else 0
        # avoid stepping into opponent territory if it also places us very close (helps counterclaim)
        danger = 4.0 if ((nx, ny) in opp_terr and d_opp <= 2) else 0.0

        val = own_gain + 0.25 * d_opp - 0.08 * t_dist - danger
        # slight preference to move (unless equal) to reduce dithering
        val += 0.01 * (1 if (dx != 0 or dy != 0) else 0)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]