def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    d0 = abs(sx - px) + abs(sy - py)

    best = (0, 0)
    best_val = -10**18

    # Targeting: nearest unclaimed if any, else push toward opponent territory, else hold.
    if unclaimed:
        targets = list(unclaimed)
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    elif opp_terr:
        targets = list(opp_terr)
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        tx, ty = sx, sy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Base value by cell status
        val = 0
        if (nx, ny) in unclaimed:
            val += 350
        if (nx, ny) in opp_terr:
            val += 120  # flipping territory on entry is valuable
        if (nx, ny) in self_terr:
            val += 15

        # Prefer reducing distance to a target (unclaimed / opponent territory)
        val += 40 * (abs(sx - tx) + abs(sy - ty) - (abs(nx - tx) + abs(ny - ty)))

        # Avoid getting too close unless we can flip
        d = abs(nx - px) + abs(ny - py)
        if (nx, ny) in opp_terr:
            val += 60  # commit to counterclaim
        else:
            val += 25 * (d - d0)  # move away when possible

        # Mild penalty near obstacles to reduce collisions/dithering
        near_obs = 0
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                ax, ay = nx + ox, ny + oy
                if (ax, ay) in obstacles:
                    near_obs += 1
        val -= 2 * near_obs

        # Tie-break deterministically: favor moves that increase max coordinate progression toward target
        if val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            # Deterministic preference order: lexicographic on (dx, dy)
            if (dx, dy) > best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]