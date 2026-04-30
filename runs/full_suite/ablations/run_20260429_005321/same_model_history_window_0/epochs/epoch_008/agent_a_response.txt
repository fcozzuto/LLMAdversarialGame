def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    rem = observation.get("remaining_resource_count", len(resources))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    cand = []
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Mode switch to change material strategy: early = contest resources, late = finish near/greedy.
    early_mode = rem > (len(resources) // 2 + 1)
    block_mode = (observation["turn_index"] % 2 == 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base score: prefer moving closer to a targeted resource.
        best = -10**18
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                # grabbing is huge
                best = max(best, 10**12)
                continue
            selfd = dist2((nx, ny), (rx, ry))
            oppd = dist2((ox, oy), (rx, ry))
            # Contest score: advantage over opponent reaching the same resource.
            contest = (oppd - selfd)
            # In late game, just greedily minimize distance.
            if not early_mode:
                score = -selfd
            else:
                # Encourage taking resources the opponent is worse off for.
                score = contest * 10 - selfd * 0.1
                # Slightly prefer nearer resources when contest is similar.
                score -= selfd * (0.01 if contest > 0 else 0.1)
            best = max(best, score)

        # Obstacle-aware: discourage getting stuck in tight corners.
        neigh_free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) not in obstacles:
                neigh_free += 1

        # Optional opponent response: if very close, try to move to increase separation while still targeting.
        opp_close = dist2((nx, ny), (ox, oy)) <= 1  # adjacent or same
        sep = -dist2((nx, ny), (ox, oy))
        opp_term = 0
        if block_mode and opp_close:
            opp_term = sep * 2

        # Small penalty for low mobility.
        mobility_pen = (2 - min(neigh_free, 2)) * 1.5

        cand.append((best + opp_term - mobility_pen, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [cand[0][1], cand[0][2]]