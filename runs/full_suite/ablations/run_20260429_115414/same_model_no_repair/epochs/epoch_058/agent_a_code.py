def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def adj_obs(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        c += 1
        return c

    # Choose a target resource we are relatively closer to (or can become closer to quickly)
    best_targets = []
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Primary: maximize closeness advantage (od - sd), then minimize our distance
        best_targets.append((od - sd, -sd, rx, ry))
    best_targets.sort(reverse=True)
    # Evaluate top few to keep simple/deterministic
    targets = [(t[2], t[3]) for t in best_targets[:min(6, len(best_targets))]]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Avoid obstacles strongly; being near obstacles often reduces maneuvering ability.
        danger = adj_obs(nx, ny)
        base = -5000 * danger

        # Compute best potential swing against opponent over chosen targets
        best_swing = -10**18
        for tx, ty in targets:
            nsd = dist(nx, ny, tx, ty)
            nod = dist(ox, oy, tx, ty)

            # If we can reach this quickly compared to opponent, prioritize it.
            # Swing rewards being closer than opponent; also reward reducing our distance.
            reach = (nod - nsd)
            swing = 3000 * reach - 10 * nsd

            # If we move onto/adjacent to a resource, add a strong deterministic bonus.
            if nsd == 0:
                swing += 200000
            elif nsd == 1:
                swing += 6000

            # Additional contest bonus if opponent is also near the resource (deny if close)
            if nod <= 2:
                swing += 2000 * (1 if nsd <= nod else -1)

            if swing > best_swing:
                best_swing = swing

        score = base + best_swing
        # Deterministic tie-break: prefer moves that reduce our Manhattan distance to opponent (sometimes helps)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cur_adv = dist(sx, sy, ox, oy)
            new_adv = dist(nx, ny, ox, oy)
            if new_adv < cur_adv:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]