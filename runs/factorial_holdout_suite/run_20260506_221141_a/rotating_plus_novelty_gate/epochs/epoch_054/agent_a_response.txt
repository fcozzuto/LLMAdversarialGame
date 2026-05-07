def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def king_dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # Immediate grab if adjacent (or staying on it)
    res_set = set(resources)
    if (sx, sy) in res_set:
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set and 0 <= nx < w and 0 <= ny < h:
            if (nx, ny) not in blocked:
                return [dx, dy]

    best_score = -10**18
    best_move = [0, 0]

    # Evaluate each move vs best target resource under a "race" score
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy

        my_next = king_dist(nx, ny, ox, oy)  # slight tie-break toward spacing
        score = 0
        for tx, ty in resources:
            d_me = king_dist(nx, ny, tx, ty)
            d_op = king_dist(ox, oy, tx, ty)
            # Prefer reaching a target sooner than opponent; otherwise prefer closest
            # Use strong weight for "me wins the race".
            race = (d_op - d_me)
            score += race * 1000 - d_me * 3 + my_next * 0.01
        # Also discourage staying still when there is progress
        if dx == 0 and dy == 0:
            score -= 5

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]