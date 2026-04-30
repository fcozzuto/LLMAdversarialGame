def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] if observation["resources"] is not None else []
    obstacles = observation["obstacles"] if observation["obstacles"] is not None else []
    obst = set((a, b) for a, b in obstacles)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h

    best = None
    best_score = None

    # Precompute obstacle penalty map (local only, cheap)
    neigh_obst = set()
    for ax, ay in obst:
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                nx, ny = ax+dx, ay+dy
                if inb(nx, ny):
                    neigh_obst.add((nx, ny))
    # Evaluate moves
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # Resource advantage: how much closer we are than opponent to the best resource
        if resources:
            max_diff = -10**9
            min_my = 10**9
            min_opp = 10**9
            for rx, ry in resources:
                myd = abs(nx - rx) + abs(ny - ry)
                opd = abs(ox - rx) + abs(oy - ry)
                if myd < min_my: min_my = myd
                if opd < min_opp: min_opp = opd
                diff = opd - myd
                if diff > max_diff: max_diff = diff
            # Combine: prioritize being closer than opponent, then being generally close
            score = 1000 * max_diff - 5 * min_my + 1 * (min_opp - min_my)
        else:
            # No resources: move toward opponent to reduce their mobility
            score = - (abs(nx - ox) + abs(ny - oy))

        # Obstacle proximity penalty and slight tendency to stay away from walls
        if (nx, ny) in neigh_obst:
            score -= 25
        score -= 0.5 * (min(nx, w-1-nx) + min(ny, h-1-ny) == 0)

        # Deterministic tie-breaking
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]