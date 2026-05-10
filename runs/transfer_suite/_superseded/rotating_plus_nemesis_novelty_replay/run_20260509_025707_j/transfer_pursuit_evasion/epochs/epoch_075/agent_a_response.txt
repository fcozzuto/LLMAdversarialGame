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

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Opponent evasion_corner pattern: they try to maximize distance from pursuer while heading toward a far corner.
    far_corner_from_opp = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    far_corner_from_me = max(corners, key=lambda c: dist2(c[0], c[1], sx, sy))
    target = far_corner_from_me if i_am_evader else far_corner_from_opp

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18 if i_am_evader else -10**18

    # Objective:
    # - If evader: maximize distance from opponent and keep heading toward farthest corner; avoid obstacles.
    # - If pursuer: minimize distance to opponent; also bias toward the evader's likely target corner for cutting off.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_target = dist2(nx, ny, target[0], target[1])

        if i_am_evader:
            # Prefer farther from opponent; smaller distance to target corner.
            val = (d_opp * 4) - (d_target * 1) + (-(abs(nx - ox) + abs(ny - oy)) * 0.01)
        else:
            # Prefer closer to opponent; also progress toward target corner.
            val = (-d_opp * 5) - (d_target * 1) + ((w * h - (abs(nx - ox) + abs(ny - oy))) * 0.0001)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move