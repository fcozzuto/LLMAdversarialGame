def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obst = set((p[0], p[1]) for p in obstacles)
    res = [tuple(p) for p in resources]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources known, drift toward center while avoiding obstacles.
    if not res:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obst:
                continue
            score = -abs(nx - cx) - abs(ny - cy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Deterministic tie-break: earlier dirs in list keep priority.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obst:
            continue
        my_pos = (nx, ny)

        # Choose the resource where we get the most distance advantage.
        local_best = -10**18
        for rx, ry in res:
            my_d = dist(my_pos, (rx, ry))
            opp_d = dist((ox, oy), (rx, ry))
            # Strongly prefer being closer than opponent; small penalty to move length.
            sc = (opp_d - my_d) * 1000 - my_d
            if sc > local_best:
                local_best = sc
        # Small preference for staying still if already on a resource cell.
        on_resource = 1 if (nx, ny) in set(res) else 0
        total = local_best + on_resource * 50 - (abs(dx) + abs(dy)) * 2
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]