def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "guard", "pursuit"))
    if not pursuer:
        pursuer = ("evader" not in self_role) or any(k in self_role for k in ("chase", "seek", "pursue"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if sx == ox and sy == oy:
        return [0, 0]

    dx_goal = 1 if ox > sx else (-1 if ox < sx else 0)
    dy_goal = 1 if oy > sy else (-1 if oy < sy else 0)

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best_move = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = dist2(nx, ny)
        diag = 1 if (abs(dx) == 1 and abs(dy) == 1) else 0
        stay = 1 if (dx == 0 and dy == 0) else 0
        align = 1 if (dx == dx_goal or dy == dy_goal) else 0

        if pursuer:
            key = (d2, -diag, stay, -align, dx, dy)
        else:
            key = (-d2, -diag, stay, -align, dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]