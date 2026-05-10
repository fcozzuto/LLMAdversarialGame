def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs_cells = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Precompute nearest opponent/unclaimed distance (cheap since we only use current sets)
    # If sets are empty, fallback to large.
    def nearest_dist(nx, ny, s):
        if not s:
            return 10**9
        md = 10**9
        for px, py in s:
            d = abs(px - nx) + abs(py - ny)
            if d < md:
                md = d
        return md

    best = None
    best_key = (-10**18, None)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs_cells:
            continue

        is_unclaimed = (nx, ny) in unclaimed
        is_self = (nx, ny) in selft
        is_opp = (nx, ny) in opp

        d_opp = nearest_dist(nx, ny, opp)
        d_un = nearest_dist(nx, ny, unclaimed)

        score = 0
        if is_opp:
            score += 12
        if is_unclaimed:
            score += 6
        if is_self:
            score += 2
        # Encourage closing in on opponent/unclaimed when not already strong targets
        score += max(0, 5 - d_opp) * (0.6 if not is_opp else 1.0)
        score += max(0, 4 - d_un) * (0.5 if not is_unclaimed else 1.0)

        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Tie-break deterministically: higher score, then nearer to opponent, then nearer to unclaimed, then center, then lexicographic move
        key = (score, -d_opp, -d_un, center_bias, -dx, -dy)
        if best is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best