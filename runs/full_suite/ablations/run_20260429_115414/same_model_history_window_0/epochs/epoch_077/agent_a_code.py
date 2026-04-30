def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    deltas = [(-1,-1), (0,-1), (1,-1),
              (-1,0),  (0,0),  (1,0),
              (-1,1),  (0,1),  (1,1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for 8-dir

    # If no resources, drift toward center while keeping away from obstacles
    if not resources:
        cx, cy = (w-1)//2, (h-1)//2
        best = (None, -10**9)
        for dx, dy in deltas:
            nx, ny = x+dx, y+dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            val = -dist((nx, ny), (cx, cy))
            if val > best[1]:
                best = ((dx, dy), val)
        return list(best[0] if best[0] is not None else (0, 0))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Target resource that gives the largest advantage vs opponent
        local_best = -10**18
        for rx, ry in resources:
            adv = dist((ox, oy), (rx, ry)) - dist((nx, ny), (rx, ry))
            # Slightly prefer closer absolute progress for us
            local = adv * 100 - dist((nx, ny), (rx, ry))
            if local > local_best:
                local_best = local

        # Add minor penalty if moving into a region around obstacles
        obs_near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx+ax, ny+ay) in obstacles:
                    obs_near += 1
        val = local_best - obs_near * 2

        # Tie-break: prefer reducing distance to opponent if competitive is equal (deny)
        opp_dist_now = dist((x, y), (ox, oy))
        opp_dist_new = dist((nx, ny), (ox, oy))
        val += (opp_dist_now - opp_dist_new) * 0.5

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]