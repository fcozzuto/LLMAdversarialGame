def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy
    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    want_pursuer = ("pursur" in self_role) or (self_role == "pursuer") or ("hunter" in self_role)
    target_dx = sign(ox - sx)
    target_dy = sign(oy - sy)

    best_move = (0, 0)
    best_key = None
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny)
        man = abs(nx - ox) + abs(ny - oy)
        diag = 1 if (dx != 0 and dy != 0) else 0
        align = 1 if (dx == target_dx and dy == target_dy) else 0
        # Additional preference: keep/approach without stepping away in both axes
        spread = (abs(nx - ox) + abs(sx - ox)) + (abs(ny - oy) + abs(sy - oy))
        if want_pursuer:
            key = (d, -diag, man, -align, spread, i)
            if best_key is None or key < best_key:
                best_key, best_move = key, (dx, dy)
        else:
            key = (-d, -diag, -man, -align, -spread, i)
            if best_key is None or key < best_key:
                best_key, best_move = key, (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]