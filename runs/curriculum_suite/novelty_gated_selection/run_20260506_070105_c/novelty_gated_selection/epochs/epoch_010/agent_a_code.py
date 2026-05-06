def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obstacles_raw)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_d = min(man(nx, ny, rx, ry) for rx, ry in resources)
        opp_d = min(man(ox, oy, rx, ry) for rx, ry in resources)

        # Base: prefer being closer than opponent to nearest resource.
        score = (opp_d - my_d) * 3

        # Tie-break: prefer reducing distance to nearest resource.
        score -= my_d

        # Small bias to keep moving toward the closest resource from current position.
        cur_my = min(man(sx, sy, rx, ry) for rx, ry in resources)
        score += (cur_my - my_d)

        # Safety: discourage staying put when a better move exists.
        if (dx, dy) == (0, 0):
            score -= 0.5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]