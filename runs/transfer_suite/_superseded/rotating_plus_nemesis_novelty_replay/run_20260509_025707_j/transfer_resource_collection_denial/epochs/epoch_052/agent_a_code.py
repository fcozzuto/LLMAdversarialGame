def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def greedy_next_dist(px, py, tx, ty):
        best = None
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not ok(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if best is None or d < best:
                best = d
        return best if best is not None else man(px, py, tx, ty)

    if not resources:
        return [0, 0]

    best_move = None  # (lead, -opp_d_next, -min_self_d, self_d_next, dx, dy)
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    for dx, dy, nx, ny in moves:
        # evaluate the best resource to secure this turn given opponent likely greedily chasing it
        best_for_move = None
        min_self_d = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            self_d = man(nx, ny, rx, ry)
            opp_d_next = greedy_next_dist(ox, oy, rx, ry)
            lead = opp_d_next - self_d
            key = (lead, -opp_d_next, -(self_d), -self_d)
            if best_for_move is None or key > best_for_move:
                best_for_move = key
            if min_self_d is None or self_d < min_self_d:
                min_self_d = self_d
        if best_for_move is None:
            continue
        # Convert to a stable ordering across resources
        self_d_next = min_self_d if min_self_d is not None else man(nx, ny, sx, sy)
        opp_d_next_best = -best_for_move[1]
        lead_best = best_for_move[0]
        final_key = (lead_best, -opp_d_next_best, -min_self_d if min_self_d is not None else 0, -self_d_next, dx, dy)
        if best_move is None or final_key > best_move:
            best_move = final_key

    return [int(best_move[4]), int(best_move[5])] if best_move is not None else [0, 0]