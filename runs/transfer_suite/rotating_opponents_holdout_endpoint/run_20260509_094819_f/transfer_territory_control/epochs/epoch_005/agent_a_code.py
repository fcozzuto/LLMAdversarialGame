def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def mindist_to_set(cx, cy, cell_set):
        if not cell_set:
            return 10**6
        md = 10**9
        for tx, ty in cell_set:
            d = abs(tx - cx) + abs(ty - cy)
            if d < md:
                md = d
        return md

    def score_move(nx, ny):
        if (nx, ny) in obstacles:
            return -10**12
        s = 0
        if (nx, ny) in unclaimed:
            s += 8
        if (nx, ny) in opp_terr:
            # Flipping is enabled on entry; only do it if it also expands frontier around it.
            s += 4
        if (nx, ny) in self_terr:
            s -= 2

        # Frontier pressure: prefer expanding near unclaimed while hugging our territory.
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                tx, ty = nx + dx, ny + dy
                if not inb(tx, ty):
                    continue
                if (tx, ty) in unclaimed:
                    s += 1
                if (tx, ty) in self_terr:
                    s += 2

                if (tx, ty) in opp_terr:
                    s -= 2  # avoid getting swarmed

                if (tx, ty) in obstacles:
                    s -= 0  # neutral; move legality already handled

        # Distance bias: keep away from opponent unless we are advancing into unclaimed.
        d_opp = abs(nx - ox) + abs(ny - oy)
        s += (d_opp // 2) * 0.2

        # If we can move closer to the overall unclaimed set, do so.
        # Use centroid-ish target: pick deterministic "closest unclaimed" direction via min dist.
        if unclaimed:
            d_now = mindist_to_set(sx, sy, unclaimed)
            d_new = mindist_to_set(nx, ny, unclaimed)
            s += (d_now - d_new) * 1.5

        return s

    best = (0, 0)
    best_sc = -10**18
    # Deterministic tie-break: fixed dir order already; additionally prefer staying still only if close.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_move(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]