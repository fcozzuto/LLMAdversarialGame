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

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        d_cur = abs(sx - ox) + abs(sy - oy)
        d_nxt = abs(nx - ox) + abs(ny - oy)

        if evader:
            # Run away: maximize distance, also avoid getting stuck in corners (keep away from walls).
            # Tie-break: prefer staying in "safer" area (more edge_dist).
            score = (d_nxt - d_cur) * 100 + d_nxt * 2 + edge_dist(nx, ny)
            # Slightly penalize moving into reduced mobility when possible (local neighbor count).
            neigh = 0
            for ddx, ddy in moves[:8]:
                tx, ty = nx + ddx, ny + ddy
                if safe(tx, ty):
                    neigh += 1
            score += neigh
            better = (best_score is None) or (score > best_score)
        else:
            # Pursuer: minimize distance; also try to reduce opponent escape by approaching while keeping move valid.
            # Tie-break: approach with diagonals naturally by distance metric; add a small bonus for staying centralized.
            score = -(d_nxt - d_cur) * 100 - d_nxt * 2 - edge_dist(nx, ny) * 0.2
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best = [dx, dy]

    if best is None:
        # If all moves blocked (unlikely), stay put deterministically.
        return [0, 0]
    return best