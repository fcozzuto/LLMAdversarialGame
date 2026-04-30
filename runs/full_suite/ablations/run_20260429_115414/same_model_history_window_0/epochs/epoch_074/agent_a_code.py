def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    rem = observation.get("remaining_resource_count", len(resources))
    # Candidate moves
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]
    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    # If few resources left, chase the nearest safely; otherwise contest by picking a resource
    # that's attractive to us but less to the opponent.
    best = None
    best_score = -10**18
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Obstacle proximity penalty (discourage moving near blocks)
        prox_pen = 0
        for ax, ay in obstacles:
            d = abs(ax - nx) + abs(ay - ny)
            if d == 0:
                prox_pen += 10
            elif d == 1:
                prox_pen += 3
            elif d == 2:
                prox_pen += 1
        # Resource scoring from next position
        if not resources:
            # No resources: move to reduce distance to opponent to deny/contest space
            score = -man((nx, ny), (ox, oy)) - 0.5*prox_pen
        else:
            # Pick best resource for this move
            local_best = -10**18
            for rx, ry in resources:
                ds = abs(rx - nx) + abs(ry - ny)
                do = abs(rx - ox) + abs(ry - oy)
                # Prefer grabbing closer; also prefer being ahead of opponent in arrival time
                grab = (60 if rem <= 4 else 30) - ds
                contest = (do - ds) * (5 if rem > 4 else 8)
                # Mild bias toward centering to avoid cornering behind obstacles
                center_bias = -(abs(rx - (w-1)/2) + abs(ry - (h-1)/2)) * 0.1
                # If we'd be standing on a resource (allowed by engine), add bonus
                on_res = 200 if (rx, ry) == (nx, ny) else 0
                val = grab + contest + center_bias + on_res - prox_pen
                if val > local_best:
                    local_best = val
            score = local_best
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]