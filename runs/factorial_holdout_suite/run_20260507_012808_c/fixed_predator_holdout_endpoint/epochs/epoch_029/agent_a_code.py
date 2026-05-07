def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    if (sx, sy) in set(resources):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose a target resource: prioritize where we are closer; if none, deny closest to opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (od - sd, -(sd + 0.001 * sd), -rx, -ry)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    # Evaluate all legal next moves; pick the one maximizing expected relative advantage.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Precompute for speed: nearest resource distances from candidate cell and opponent.
    resources_list = resources
    best_move = None
    best_score = None
    for dx, dy, nx, ny in moves:
        # Main term: race on chosen target
        n_self = abs(rx - nx) + abs(ry - ny)
        n_opp = abs(rx - ox) + abs(ry - oy)
        score = (n_opp - n_self) * 10.0

        # Secondary term: if we get closer to any resource, it helps; if opponent is closer, it hurts.
        # Use min distances for determinism and brevity.
        min_self = None
        min_opp = None
        for (tx, ty) in resources_list:
            ds = abs(tx - nx) + abs(ty - ny)
            do = abs(tx - ox) + abs(ty - oy)
            if min_self is None or ds < min_self:
                min_self = ds
            if min_opp is None or do < min_opp:
                min_opp = do
        score += (min_opp - min_self) * 1.5

        # Slight penalty for staying (encourage movement unless already good)
        if dx == 0 and dy == 0:
            score -= 0.25

        # Deterministic tie-break using target direction alignment
        align = (1 if (nx - sx) * (rx - sx) >= 0 else -1) + (1 if (ny - sy) * (ry - sy) >= 0 else -1)
        score += 0.01 * align

        key = score
        if best_score is None or key > best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move