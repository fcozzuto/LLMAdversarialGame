def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Deterministic target corner selection
    if i_am_evader:
        target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        target_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best_move = (0, 0)
    best_val = None

    # Parity penalty to reduce dithering in deterministic pursuit/evasion
    my_parity = (sx + sy) & 1
    op_parity = (ox + oy) & 1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, target_corner[0], target_corner[1])
        parity = ((nx + ny) & 1)

        if i_am_evader:
            val = (-d_opp) + 0.10 * d_corner + 0.05 * (parity ^ op_parity) + 0.02 * (abs(dx) + abs(dy))
            # maximize d_opp => minimize val
        else:
            val = d_opp + 0.20 * d_corner + 0.05 * (parity ^ my_parity) + 0.02 * (abs(dx) + abs(dy))
            # minimize d_opp => minimize val

        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]