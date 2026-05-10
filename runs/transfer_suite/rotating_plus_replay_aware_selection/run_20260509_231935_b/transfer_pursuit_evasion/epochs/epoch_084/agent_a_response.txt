def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    move_list = []
    for m in order:
        if m in moves:
            move_list.append(m)
    for m in moves:
        if m not in move_list:
            move_list.append(m)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_score = None
    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)

        if pursuer:
            # Primary: minimize distance. Secondary: prefer moving toward opponent in at least one axis.
            axis_toward = (1 if (nx != ox) else 0) + (1 if (ny != oy) else 0)
            score = (-d, -axis_toward, -abs((nx - sx)) - abs((ny - sy)))
        else:
            # Evader: maximize distance. Secondary: maximize mobility to avoid getting cornered.
            mobility = 0
            for ddx, ddy in moves:
                nnx, nny = nx + ddx, ny + ddy
                if valid(nnx, nny):
                    mobility += 1
            score = (d, mobility, -abs(nx - sx) - abs(ny - sy))

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]