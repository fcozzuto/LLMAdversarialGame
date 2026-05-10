def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if unclaimed:
        # Choose nearest unclaimed; tie-break deterministically by tuple
        target = min(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        # If none, target nearest opponent territory cell to allow potential flip/contest
        if opp_terr:
            target = min(opp_terr, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
        else:
            # Otherwise, hold position
            return [0, 0]

    tx, ty = target

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Base objective: move closer to target
        dist = abs(nx - tx) + abs(ny - ty)
        val = -dist * 5

        # Territory control incentives
        if (nx, ny) in unclaimed:
            val += 220
        if (nx, ny) in self_terr:
            val += 18
        if (nx, ny) in opp_terr:
            val += 95  # flipping on entry

        # Prefer moves that reduce distance to opponent if we can flip/contest
        opp_dist = abs(nx - px) + abs(ny - py)
        val += max(0, 20 - opp_dist) * 0.6

        # Discourage stepping into immediate "bad" diagonal traps near obstacles
        # (cheap local check)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if inb(xx, yy) and (xx, yy) in obstacles:
                    adj_obs += 1
        val -= adj_obs * 4

        # Deterministic tie-breaker
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]