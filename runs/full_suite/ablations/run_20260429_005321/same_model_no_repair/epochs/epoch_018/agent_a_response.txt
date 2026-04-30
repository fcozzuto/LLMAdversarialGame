def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        return [dx, dy]

    # Pick a deterministic target: closest resource, tie-break by farther from opponent
    resources_sorted = sorted(resources, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), -(abs(p[0]-ox)+abs(p[1]-oy)), p[0], p[1]))
    tx, ty = resources_sorted[0]

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_target = abs(tx - nx) + abs(ty - ny)
        # Encourage increasing distance from opponent unless we're also improving target distance
        d_opp = abs(ox - nx) + abs(oy - ny)
        # Mild penalty for stepping adjacent to opponent (denies taking turns/contested zones)
        adj_pen = 4 if max(abs(ox - nx), abs(oy - ny)) <= 1 and (ox, oy) != (nx, ny) else 0
        # Avoid moving into squares that are also very close to many resources (likely contest)
        close_resources = 0
        for rx, ry in resources_sorted[:6]:
            if abs(rx - nx) + abs(ry - ny) <= 2:
                close_resources += 1

        # Lower is better
        val = d_target * 10 - d_opp * 1.5 + adj_pen * 2 + close_resources * 3

        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]