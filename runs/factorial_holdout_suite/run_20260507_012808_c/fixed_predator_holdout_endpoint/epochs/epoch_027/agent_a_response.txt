def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    resources = list(dict.fromkeys(resources))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # If we're on a resource, prefer staying (deterministically) to secure it.
    if (sx, sy) in set(resources):
        return [0, 0]

    opp_set = {(ox, oy)}
    best_move = None
    best_key = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Score the move by the best resource we can secure relative to the opponent.
        # Higher is better: (opp_dist - self_dist) first, then closer self_dist, then deterministic coords.
        best_for_move = None
        for rx, ry in resources:
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            margin = opp_d - self_d
            # Small penalty for entering opponent's exact cell (should rarely be legal/meaningful).
            penalty = 1 if (nx, ny) in opp_set else 0
            key = (margin, -self_d, -penalty, rx, ry)
            if best_for_move is None or key > best_for_move:
                best_for_move = key

        # Prefer moves that don't yield a "worse-than-opponent" situation when avoider opponent can contest.
        # Tie-break: minimize distance to best resource for consistency.
        move_key = (best_for_move[0], best_for_move[1], best_for_move[2], best_for_move[3], best_for_move[4], dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]