def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer moves that secure resources where we are not behind, otherwise deny by approaching
    # the best contestable resource while staying away from opponent.
    def adj_obs_count(x, y):
        c = 0
        for ax in (-1,0,1):
            for ay in (-1,0,1):
                if ax == 0 and ay == 0:
                    continue
                if (x+ax, y+ay) in obstacles:
                    c += 1
        return c

    center = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = None

    # Sort resources deterministically for stable tie-breaks
    resources = sorted(resources)

    for dx, dy, nx, ny in legal:
        # Base: stay safer from opponent and avoid obstacle proximity
        oppd = manh(nx, ny, ox, oy)
        cdx = nx - center[0]
        cdy = ny - center[1]
        center_bias = -0.05 * (cdx*cdx + cdy*cdy)
        score = 1.5 * oppd + center_bias - 0.35 * adj_obs_count(nx, ny)

        if resources:
            # Find best resource according to "lead" (opp_dist - self_dist), tie by lower self_dist then lexicographic
            local_best = None
            local_key = None
            for rx, ry in resources:
                ds = manh(nx, ny, rx, ry)
                do = manh(ox, oy, rx, ry)
                lead = do - ds
                # prefer resources we can contest: positive lead first
                # key: higher lead, then smaller ds, then lexicographic
                key = (-(lead), ds, rx, ry)
                if local_key is None or key < local_key:
                    local_key = key
                    local_best = (lead, ds, rx, ry)
            lead, ds, rx, ry = local_best
            # If we are behind (lead negative), still move toward resource that minimizes deficit
            score += 2.0 * max(lead, 0) + 0.8 * lead - 0.02 * ds
            # Lightly discourage walking into a "race" where opponent is already extremely close
            score -= 0.03 * manh(ox, oy, nx, ny)

        key2 = (-score, dx, dy)  # deterministic tie-break
        if best_score is None or key2 < best_score:
            best_score = key2
            best = (dx, dy)

    return [int(best[0]), int(best[1])]