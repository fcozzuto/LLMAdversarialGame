def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for x, y in resources:
        our_t = kdist(sx, sy, x, y)
        opp_t = kdist(ox, oy, x, y)
        # Prefer guaranteed grabs; otherwise steal by being closer, while avoiding states where opponent is closer after we commit.
        win = our_t < opp_t
        diff = opp_t - our_t
        # Corner bias to break ties deterministically.
        corner_bias = (0 if (x == 0 or x == w - 1) else 1) + (0 if (y == 0 or y == h - 1) else 1)
        key = (0 if win else 1, -diff, our_t, corner_bias, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate by resulting distance to target, with penalty if it makes opponent relatively closer to the same target.
        our_d = kdist(nx, ny, tx, ty)
        opp_d = kdist(ox, oy, tx, ty)
        # tie-break with raw position for determinism
        score = (our_d, opp_d - our_d, abs((nx - tx)) + abs((ny - ty)), nx, ny)
        if best_eval is None or score < best_eval:
            best_eval = score
            best_move = [dx, dy]

    # If all moves blocked, stay.
    return best_move if best_move is not None else [0, 0]