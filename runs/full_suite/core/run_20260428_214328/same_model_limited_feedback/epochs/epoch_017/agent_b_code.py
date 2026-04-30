def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    rem = observation.get("remaining_resource_count", len(resources))
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b, c, d): 
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy
    def clamp_move(x, y):
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return (dx, dy)
        return (0, 0)

    # If resources are scarce, switch to contesting the opponent directly.
    if rem <= 3:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            v = -dist2(nx, ny, ox, oy)  # minimize distance to opponent
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Otherwise, go for the resource where we have the clearest first-reach advantage.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Small penalty for getting too close to opponent to avoid collisions/blocks.
        opp_prox = dist2(nx, ny, ox, oy)
        score = -0.02 * opp_prox

        # Evaluate best contested resource from the candidate position.
        # Advantage = (opponent distance - my distance): higher means I reach earlier.
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist2(nx, ny, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            adv = opd - myd
            # If we land on resource, strongly prefer.
            if myd == 0:
                score += 1000000 + adv
            else:
                score += adv * 0.001

        # Add a tiny tie-break: prefer moves that move closer to the best resource overall.
        # Deterministic: compute min myd after move.
        mind = 10**18
        for rx, ry in resources:
            myd = dist2(nx, ny, rx, ry)
            if myd < mind:
                mind = myd
        score += -0.00001 * mind

        if score > bestv:
            bestv = score
            best = (dx, dy)

    # If all candidate moves invalid (unlikely), stay.
    return [best[0], best[1]]