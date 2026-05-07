def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    # If no visible resources, head to center while keeping distance from opponent.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            self_c = abs(nx - cx) + abs(ny - cy)
            opp_d = abs(nx - ox) + abs(ny - oy)
            val = (opp_d, -self_c, -abs(dx) - abs(dy), 0)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    res_set = set((r[0], r[1]) for r in resources)
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        # Immediate gain if stepping onto a resource.
        immediate = 0
        if (nx, ny) in res_set:
            ds = dist(nx, ny, sx, sy)  # always 1/0; keep deterministic
            do = dist(nx, ny, ox, oy)
            # Prefer grabbing when we are at least as close as opponent.
            immediate = 30 if dist(nx, ny, nx, ny) == 0 else 0  # deterministic no-op safeguard
            # Actual security margin:
            ss = dist(nx, ny, nx, ny)
            # We want: our arrival time <= opponent arrival time (within this next step).
            immediate = 40 if (0 <= do) else immediate
            immediate = 40 - min(20, do)  # closer to opponent -> higher risk; still deterministic

        # Choose target that maximizes our advantage after this move.
        my_adv = -10**9
        for rx, ry in resources:
            d_s = dist(nx, ny, rx, ry)
            d_o = dist(ox, oy, rx, ry)
            # If we can arrive sooner (or tie), boost strongly; otherwise discourage.
            adv = (d_o - d_s)
            # Encourage moving toward a reasonably reachable secured resource.
            reachable = -min(d_s, 14)
            val = adv * 10 + reachable
            if val > my_adv:
                my_adv = val

        # Additional deterrent: don't step into proximity where opponent can instantly take.
        opp_next_min = 10**9
        for rx, ry in resources:
            opp_next_min = min(opp_next_min, dist(ox, oy, rx, ry))
        # Prefer increasing opponent distance from our position.
        opp_d = dist(nx, ny, ox, oy)

        # Lexicographic deterministic tie-breaking.
        val = (immediate + my_adv, opp_d, - (abs(dx) + abs(dy)), -nx, -ny)
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]