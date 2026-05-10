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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Deterministic tie-break: fixed order of moves and a small lexicographic bias to keep behavior stable.
    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d_cur = abs(sx - ox) + abs(sy - oy)
        d_nxt = abs(nx - ox) + abs(ny - oy)

        # Also encourage moves that keep away from edges when evading (prevents boundary-sticking).
        edge_dist = min(nx, ny, (w - 1 - nx), (h - 1 - ny))

        # Immediate objective
        if evader:
            # Maximize survival: increase distance; also avoid collapsing toward opponent's direction.
            away_x, away_y = nx - ox, ny - oy
            dot = away_x * (ox - sx) + away_y * (oy - sy)  # positive means moving with away direction
            val = (d_nxt, dot, edge_dist, -(abs(nx - (w - 1)) + abs(ny - (h - 1))))
            better = (best_val is None) or (val > best_val)
        else:
            # Pursuer: minimize distance; prefer moves that reduce opponent-escape potential via "alignment".
            align = (nx - sx) * (ox - sx) + (ny - sy) * (oy - sy)  # toward opponent direction
            val = (-d_nxt, align, edge_dist, -(abs(nx - 0) + abs(ny - 0)))
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]