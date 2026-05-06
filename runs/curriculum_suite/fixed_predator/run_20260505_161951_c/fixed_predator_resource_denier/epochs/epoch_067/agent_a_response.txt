def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        best = (0, 0); bestv = -10**18
        tx, ty = w - 1, h - 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 - (abs(nx - tx) + abs(ny - ty)) - (1 if (nx, ny) in obs else 0)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    res_set = set((a, b) for a, b in resources)
    tx, ty = w - 1, h - 1
    # Use a "switching" evaluation: try to create a large reach-time gap vs opponent on the best resource,
    # with a denial component for resources where opponent is closer.
    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) in res_set:
            v = 10**9 - (cheb(nx, ny, tx, ty) // 2)
        else:
            # Evaluate against up to a small deterministic subset of resources (closest-by-cheb to reduce noise).
            # Choose subset by deterministic order: nearest to us, then nearest to opponent.
            scored = []
            for rx, ry in resources:
                scored.append((cheb(nx, ny, rx, ry), cheb(ox, oy, rx, ry), rx, ry))
            scored.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
            top = scored[:min(4, len(scored))]

            v = -10**18
            for sd, od, rx, ry in top:
                # Advantage if we are closer (positive), denial pressure if opponent is closer.
                adv = (od - sd)  # higher means we likely beat them
                deny = (sd - od)  # negative when we are behind
                # Prefer pushing toward resources and also keep some progress toward bottom-right.
                progress = -(abs(rx - tx) + abs(ry - ty))
                cand = adv * 120 + deny * 20 + progress
                if cand > v: v = cand

            # Small tie-breakers: avoid getting too close to obstacles' clusters and prefer moving generally toward target.
            v += -(abs(nx - x) + abs(ny - y)) * 0.5
            v += -(abs(nx - tx) + abs(ny - ty)) * 0.01

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v; best = (dx, dy)

    return [best[0], best[1]]