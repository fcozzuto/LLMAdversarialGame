def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Prefer moving to resources where we gain over the opponent; when we can't win races,
        # try to move into good "denial" positions that make opponent's nearest progress worse.
        local_best = None
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry) if opp_exists else 10**6
            # Large weight on (opp_d - my_d): we want to be earlier; then tie-break on my_d.
            # Add small bias toward resources closer to the center early to avoid getting stuck.
            center_bias = - (abs(rx - (w - 1) // 2) + abs(ry - (h - 1) // 2))
            score = (opp_d - my_d) * 1000 + center_bias - my_d
            # deterministic tie-break
            key = (-score, my_d, opp_d, dx, dy)
            if local_best is None or key < local_best[0]:
                local_best = (key, score)
        if local_best is None:
            continue
        if best_key is None or local_best[0] < best_key:
            best_key = local_best[0]
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move