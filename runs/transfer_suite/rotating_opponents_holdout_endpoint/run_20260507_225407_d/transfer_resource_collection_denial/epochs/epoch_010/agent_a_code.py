def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = [0, 0]
    bestv = -10**18

    # Precompute opponent distances to resources for cheap comparison
    oppd = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        oppd.append((rx, ry, cheb(ox, oy, rx, ry)))

    if not oppd:
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh:
            continue
        if (nx, ny) in obstacles:
            continue

        # Score this move by the best resource "win margin" it creates
        v = -10**18
        for rx, ry, do in oppd:
            ds = cheb(nx, ny, rx, ry)
            # Encourage moving to resources where we are strictly earlier
            margin = do - ds  # positive is good
            # If we're not earlier (tie/lose), heavily devalue
            if margin <= 0:
                cand = -200 - ds
            else:
                # Prefer larger margin; also slightly prefer closer ds for getting there soon
                cand = margin * 800 - ds * 3

            # Additional penalty if opponent could still reach that resource no later than us next step
            opp_next_bound = do  # opponent position is fixed this turn
            if opp_next_bound <= ds + 0:
                cand -= 120

            if cand > v:
                v = cand

        # Secondary tie-break: reduce distance to the closest resource overall
        if v > bestv:
            bestv = v
            best = [dx, dy]
        elif v == bestv:
            # Deterministic: choose lexicographically smaller [dx,dy]
            if [dx, dy] < best:
                best = [dx, dy]

    return best