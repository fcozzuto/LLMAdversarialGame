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
    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]
    tr = observation.get("turns_remaining", 0)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_after = 0
        score_for_moves = -10**18

        for r in resources:
            rx, ry = r[0], r[1]
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            # Strongly prefer resources where we become closer than the opponent.
            gap = opp_d - my_d
            # Prefer nearer targets and earlier collection.
            early = 3 if (tr <= 0 or my_d <= tr) else 0
            val = gap * 50 - my_d * 3 + early
            # Slightly diversify away from single-resource chasing if already very close.
            if my_d == 0:
                val += 2000
            if val > score_for_moves:
                score_for_moves = val
                my_after = my_d

        # If tie, prefer smaller my distance to chosen target (more robust collection).
        if score_for_moves > best_val:
            best_val = score_for_moves
            best_move = [dx, dy]
        elif score_for_moves == best_val:
            if my_after < dist(sx, sy, best_move[0] + sx, best_move[1] + sy):
                best_move = [dx, dy]

    return best_move