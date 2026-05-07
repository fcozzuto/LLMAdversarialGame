def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_val = -10**18
    best_self_d = 10**9
    best_tx, best_ty = None, None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        chosen_val = -10**18
        chosen_self_d = 10**9
        chosen_tx, chosen_ty = None, None

        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)

            # Swing: positive when we are closer than opponent to this resource.
            swing = opp_d - self_d

            # Prefer resources we can potentially reach first; emphasize denial when opponent is closer.
            # Also lightly prefer generally closer resources.
            val = (swing * 20) - (self_d * 2) + (10 if swing > 0 else 0) + (6 if opp_d <= self_d else 0)

            if val > chosen_val or (val == chosen_val and (self_d < chosen_self_d or (self_d == chosen_self_d and (rx, ry) < (chosen_tx, chosen_ty) if chosen_tx is not None else True))):
                chosen_val = val
                chosen_self_d = self_d
                chosen_tx, chosen_ty = rx, ry

        if chosen_val > best_val or (chosen_val == best_val and (chosen_self_d < best_self_d or (chosen_self_d == best_self_d and (dx, dy) < best_move))):
            best_val = chosen_val
            best_self_d = chosen_self_d
            best_move = (dx, dy)
            best_tx, best_ty = chosen_tx, chosen_ty

    dx, dy = best_move
    return [int(dx), int(dy)]