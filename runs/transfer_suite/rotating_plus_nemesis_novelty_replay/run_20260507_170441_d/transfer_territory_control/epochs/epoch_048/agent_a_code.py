def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_cells = list(opp_t) if opp_t else []
    unclaimed_list = list(unclaimed) if unclaimed else []

    def nearest_dist_to_set(px, py, s):
        md = 10**9
        for x, y in s:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    # Target: unclaimed cells that are adjacent to (or close to) opponent territory to counterclaim efficiently.
    if unclaimed_list and opp_cells:
        best_target = None
        best_td = 10**18
        for x, y in unclaimed_list:
            td = min(abs(ax - x) + abs(ay - y) for ax, ay in opp_cells)  # small grids; deterministic
            if td < best_td:
                best_td = td
                best_target = (x, y)
        tx, ty = best_target
    elif unclaimed_list:
        tx, ty = min(unclaimed_list, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    elif opp_cells:
        tx, ty = min(opp_cells, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = ox, oy  # fallback

    # Prefer entering opponent-owned cells when they are directly reachable and close to the chosen target.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy
            dx, dy = 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v += 800
            # If flipping, bias toward the direction that reduces distance to the target.
            v += 60 - 10 * (abs(nx - tx) + abs(ny - ty))
        elif (nx, ny) in unclaimed:
            v += 250
            v += 30 - 5 * (abs(nx - tx) + abs(ny - ty))
        elif (nx, ny) in self_t:
            v += 40
            v += 10 - 3 * (abs(nx - tx) + abs(ny - ty))

        # Keep pressure near the opponent: reduce distance to opponent territory but not suicidal wandering.
        if opp_cells:
            d_opp = min(abs(ax - nx) + abs(ay - ny) for ax, ay in opp_cells)
            v += 120 - 12 * d_opp
            # Discourage moving away from target.
            v += 20 - 4 * (abs(nx - tx) + abs(ny - ty))
        else:
            v += 50 - 5 * (abs(nx - tx) + abs(ny - ty))

        # Mild anti-stall: if we are not in a good cell, discourage staying unless forced.
        if dx == 0 and dy == 0:
            v -= 35

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return best