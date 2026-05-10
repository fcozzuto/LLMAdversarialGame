def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def centroid(cset):
        if not cset:
            return (w - 1, h - 1)
        xs = [p[0] for p in cset]
        ys = [p[1] for p in cset]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    ocx, ocy = centroid(opp_t)

    frontier = []
    for (x, y) in (self_t | unclaimed):
        if (x, y) in obstacles:
            continue
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny) and (nx, ny) in opp_t:
                        frontier.append((x, y))
                        dx = dy = 2
                        break
            if len(frontier) and frontier[-1] == (x, y):
                break

    def cell_score(x, y):
        if not inside(x, y) or (x, y) in obstacles:
            return -10**9
        if (x, y) in self_t:
            return -5  # don't waste time staying inside unless needed
        base = 0
        if (x, y) in unclaimed:
            base += 60
        if (x, y) in opp_t:
            base += 100  # flipping on entry
        # Move toward opponent centroid, but prefer contacting opponent territory.
        dist = abs(x - ocx) + abs(y - ocy)
        base += -0.8 * dist
        adj_opp = 0
        adj_uncl = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny):
                        if (nx, ny) in opp_t:
                            adj_opp += 1
                        if (nx, ny) in unclaimed:
                            adj_uncl += 1
        base += 8 * adj_opp + 2.5 * adj_uncl
        # Encourage expansion away from obstacles by mild penalty if near obstacle
        near_obs = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny) and (nx, ny) in obstacles:
                        near_obs += 1
        base -= 3 * near_obs
        return base

    actions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)
    # Deterministic tie-break: prefer moves with greater |dx|+|dy|? then fixed order.
    for i, (dx, dy) in enumerate(actions):
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        if sc > best[0]:
            best = (sc, dx, dy)
        elif sc == best[0]:
            if (abs(dx) + abs(dy), -i) > (abs(best[1]) + abs(best[2]), -actions.index((best[1], best[2]))):
                best = (sc, dx, dy)
    return [int(best[1]), int(best[2])]