def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    # Deterministic preference weights
    best_move = [0, 0]
    best_score = None

    d_cur = abs(sx - ox) + abs(sy - oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_nxt = abs(nx - ox) + abs(ny - oy)

        # Large primary term to chase/flee; secondary terms to avoid getting trapped.
        m = mobility(nx, ny)
        e = edge_dist(nx, ny)

        if evader:
            # Keep distance and preserve mobility; prefer not to hug walls.
            score = (d_nxt - d_cur) * 1000 + m * 10 + e
        else:
            # Reduce distance and preserve mobility; prefer center-ish to avoid corridors.
            score = (d_cur - d_nxt) * 1000 + m * 10 + e

        # Avoid immediate collision if possible (for evader) / prefer it if pursuer.
        if not evader and (nx == ox and ny == oy):
            score += 1e6
        if evader and (nx == ox and ny == oy):
            score -= 1e6

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]