def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def neighbors_free(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    cnt += 1
        return cnt

    opp_dist_to_target_min = None
    # Strategy pivot: early game "race" resources we can beat, late game "chase blocking" (avoid letting opponent get ahead)
    remaining = int(observation.get("remaining_resource_count", len(resources)) or 0)
    late = 1 if remaining <= 5 else 0

    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # main: prefer cells we are closer to than opponent
        lead = od - sd
        # secondary: avoid targets opponent is much closer to (especially late game)
        danger = sd - od  # negative means opponent closer
        # tertiary: nudge toward regions with more freedom (less likely stuck)
        freedom = neighbors_free(rx, ry)
        key = (
            lead - late * max(0, -danger),   # race when early, deny when late
            freedom,
            -sd,
            -rx,
            -ry
        )
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    move_options = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                my_d = man(nx, ny, tx, ty)
                op_d = man(ox, oy, tx, ty)
                # Also add a tiny tie-breaker to reduce congestion near obstacles (prefer more freedom)
                freedom = neighbors_free(nx, ny)
                key = (
                    (op_d - my_d) + late * (my_d - op_d <= 0) * 0.1,  # prefer maintaining/creating lead
                    -my_d,
                    freedom,
                    -abs((nx - ox)) - abs((ny - oy))
                )
                move_options.append((key, dx, dy))

    if not move_options:
        return [0, 0]
    move_options.sort(reverse=True)
    return [int(move_options[0][1]), int(move_options[0][2])]