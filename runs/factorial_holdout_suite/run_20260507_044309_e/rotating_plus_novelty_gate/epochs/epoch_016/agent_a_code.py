def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))

    # When opponent is denier-like, prioritize resources where we can beat their reach,
    # otherwise move to an "intercept" position near the closest competitive resource.
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        our_best = 10**9
        opp_best = 10**9
        block_best = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_our = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)

            # Dominance: negative is good (we're closer after our move).
            dom = d_our - d_opp
            if dom < our_best:
                our_best = dom
            if d_our < opp_best:
                opp_best = d_our

            # Intercept heuristic: if opponent is much closer, move to reduce their gap by
            # aiming near their next approach direction (approx via diagonal step to resource).
            if d_opp <= d_our:
                # Expected step direction from opponent toward resource
                stepx = 0 if ox == rx else (1 if rx > ox else -1)
                stepy = 0 if oy == ry else (1 if ry > oy else -1)
                ix, iy = rx - stepx, ry - stepy  # a cell just before the resource
                if inb(ix, iy):
                    d_block = man(nx, ny, ix, iy)
                    # Prefer smaller block distance, but only for resources where we're behind.
                    if d_block < block_best:
                        block_best = d_block
        # Combine: primary dominance, then immediate pickup distance, then interception when behind.
        remaining = observation.get("remaining_resource_count", len(resources))
        intercept_weight = 3 if remaining > 4 else 1
        score = (our_best, opp_best + intercept_weight * (block_best if block_best < 10**9 else 0))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]