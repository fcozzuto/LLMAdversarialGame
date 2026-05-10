def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if unclaimed:
        # choose nearest unclaimed as expansion target
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))
    else:
        tx, ty = ox, oy

    base_to_opp = abs(sx - ox) + abs(sy - oy)
    base_to_t = abs(sx - tx) + abs(sy - ty)

    best = (0, 0)
    best_score = -10**18
    best_tieb = None

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 800
        if (nx, ny) in unclaimed:
            score += 70
        if (nx, ny) in self_t:
            score += 8

        # Prefer moving toward unclaimed target; also prefer distancing from opponent unless capturing opp.
        dt = abs(nx - tx) + abs(ny - ty)
        do = abs(nx - ox) + abs(ny - oy)
        score += (base_to_t - dt) * 6
        score += (do - base_to_opp) * 2
        # Slightly prefer lateral moves that keep options open (fewer obstacle collisions around the target cell)
        neigh_free = 0
        for ex, ey in dirs:
            xx, yy = nx + ex, ny + ey
            if 0 <= xx < w and 0 <= yy < h and (xx, yy) not in obstacles:
                neigh_free += 1
        score += neigh_free * 0.5

        tieb = (-(ddx == 0 and ddy == 0), -nx, -ny)  # deterministic tie-break: avoid stalling first
        if score > best_score or (score == best_score and (best_tieb is None or tieb < best_tieb)):
            best_score = score
            best_tieb = tieb
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]