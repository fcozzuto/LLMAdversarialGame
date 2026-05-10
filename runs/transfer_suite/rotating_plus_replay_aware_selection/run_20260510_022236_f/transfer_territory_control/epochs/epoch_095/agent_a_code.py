def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Conservative heuristic: prioritize flipping opponent territory near us, then unclaimed expansion,
    # then maintaining our territory. Bias slightly toward expanding toward the frontier.
    total_unclaimed = len(unclaimed)
    up = int(observation.get("self_territory_count") or 0)
    op = int(observation.get("opponent_territory_count") or 0)
    we_lead = up >= op

    # Compute a simple frontier direction: look for the nearest cell among unclaimed+opponent to pull toward.
    frontier_targets = []
    if total_unclaimed:
        frontier_targets = list(unclaimed)
    if not frontier_targets:
        frontier_targets = list(op_terr)
    if not frontier_targets:
        frontier_targets = list(self_terr)

    def nearest_dist(x, y):
        if not frontier_targets:
            return 0
        best = 10**9
        # small deterministic scan cap
        cap = len(frontier_targets) if len(frontier_targets) < 48 else 48
        for i in range(cap):
            cx, cy = frontier_targets[i]
            d = abs(cx - x) + abs(cy - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best if best != 10**9 else 0

    cur_dist = nearest_dist(sx, sy)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        if cell in self_terr:
            base = 1.0
        elif cell in op_terr:
            base = 4.5  # flipping on entry is enabled
        elif cell in unclaimed:
            base = 3.5
        else:
            base = 0.5  # could be empty/other controlled boundary

        # Frontier improvement term
        nd = nearest_dist(nx, ny)
        # Prefer getting closer to frontier (or at least not increasing too much)
        frontier_term = (cur_dist - nd) * 0.25

        # If we're sole leader at leader bonus turn, keep pressure instead of risky moves
        # (approx: penalize entering opponent territory if it would not improve distance)
        bonus_penalty = 0.0
        if we_lead and op < up and (int(observation.get("turn_index") or 0) % 10 == 9):
            if cell in op_terr and (nd >= cur_dist):
                bonus_penalty = -1.2

        score = base + frontier_term + bonus_penalty

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best