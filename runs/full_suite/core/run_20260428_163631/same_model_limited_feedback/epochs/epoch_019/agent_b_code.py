def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target selection: pick resource where we're relatively closer than opponent.
    best_r = resources[0]
    best_v = None
    for r in resources:
        ds = man((sx, sy), r)
        do = man((ox, oy), r)
        v = ds - do
        if best_v is None or v < best_v or (v == best_v and (r[0] + r[1], r[0], r[1]) < (best_r[0] + best_r[0], best_r[0], best_r[1])):
            best_v = v
            best_r = r

    # Move selection: evaluate 9 deterministic moves.
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_score = None

    # Secondary: encourage spreading away from opponent unless it harms reaching target.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_t = man((nx, ny), best_r)
        d_to_opp = man((nx, ny), (ox, oy))

        # If near target, prefer it; otherwise prefer relative advantage and opponent separation.
        # Small obstacle-aware term: prefer moves with fewer adjacent obstacles.
        adj_obs = 0
        for ax in (-1,0,1):
            for ay in (-1,0,1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                    adj_obs += 1

        score = (-10 * d_to_t) + (0.5 * d_to_opp) - (0.2 * adj_obs)

        # Deterministic tie-break: prefer closer to target, then higher separation, then lexicographic delta.
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            cand = (d_to_t, -d_to_opp, dx, dy)
            cur = (man((sx + best_move[0], sy + best_move[1]), best_r), -man((sx + best_move[0], sy + best_move[1]), (ox, oy)), best_move[0], best_move[1])
            if cand < cur:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]