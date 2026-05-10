def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    unT = set((int(x), int(y)) for x, y in unclaimed)

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Select a target deterministically: prefer cells closest to opponent, but reachable candidates only.
    candidates = []
    for x, y in unT:
        if inb(x, y):
            candidates.append((x, y))
    for x, y in opT:
        if inb(x, y) and (x, y) not in selfT:
            candidates.append((x, y))

    if candidates:
        # bias toward cells near opponent while not ignoring proximity to us
        tx, ty = min(candidates, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), abs(c[0] - sx) + abs(c[1] - sy)))
    else:
        tx, ty = ox, oy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Heuristic: progress to target + reward flipping/claiming
        dist_now = abs(sx - tx) + abs(sy - ty)
        dist_new = abs(nx - tx) + abs(ny - ty)
        progress = dist_now - dist_new

        flip_reward = 0
        if (nx, ny) in opT:
            flip_reward += 6
        elif (nx, ny) in unT:
            flip_reward += 3
        elif (nx, ny) in selfT:
            flip_reward -= 1

        # Slightly pressure away from being trapped by obstacles: fewer obstacle-adjacent cells preferred
        adj_obs = 0
        for ax, ay in dirs:
            xx, yy = nx + ax, ny + ay
            if 0 <= xx < w and 0 <= yy < h and (xx, yy) in obs:
                adj_obs += 1

        score = 10 * progress + flip_reward - 0.2 * adj_obs
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move