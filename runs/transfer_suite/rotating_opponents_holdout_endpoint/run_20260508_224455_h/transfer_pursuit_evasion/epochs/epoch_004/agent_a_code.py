def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    self_role = str(observation.get("self_role", "")).lower()
    i_am_pursuer = ("pursuer" in self_role) or ("pursue" in self_role)
    if "evader" in self_role or "evade" in self_role:
        i_am_pursuer = False

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and not blocked(nx, ny):
                c += 1
        return c

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = dist2(nx, ny)
        mob = mobility(nx, ny)

        # Small, deterministic tie-breakers using coordinates and role direction
        # If pursuer: minimize distance; if evader: maximize distance.
        if i_am_pursuer:
            val = (-d, -mob, abs(ox - nx) + abs(oy - ny), (nx + 7 * ny))
        else:
            val = (d, -mob, -(abs(ox - nx) + abs(oy - ny)), -(nx + 7 * ny))

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]