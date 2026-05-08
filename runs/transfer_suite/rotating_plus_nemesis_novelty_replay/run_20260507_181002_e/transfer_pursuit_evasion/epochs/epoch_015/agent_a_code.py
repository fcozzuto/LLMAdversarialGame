def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    my_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            my_moves.append((dx, dy))
    if not my_moves:
        return [0, 0]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in dirs:
            if free(x + dx, y + dy):
                c += 1
        return c

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    pursuer = ("pursuer" in srole) or ("catch" in srole) or ("chaser" in srole) or ("pursuit" in srole) or ("tag" in srole and "evad" not in srole)
    if "evader" in srole or "evad" in srole:
        pursuer = False
    if "pursuer" in orole and ("evader" in srole or "evad" in srole):
        pursuer = False

    # Wall-run bias for evasion: prefer keeping progress along top/bottom edges on odd turns.
    ti = observation.get("turn_index", 0)
    wall_pref = (ti % 2 == 0)

    best = None
    best_val = None
    for dx, dy in my_moves:
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny, ox, oy)
        m = mobility(nx, ny)

        # obstacle proximity penalty (deterministic, cheap)
        prox = 0
        for ax, ay in obstacles:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1:
                prox += 1

        if pursuer:
            # Push to reduce distance; also prefer higher mobility / less obstacle adjacency.
            val = -d + 0.15 * m - 0.3 * prox
            # slight tie-break: aim for non-staying moves
            if dx == 0 and dy == 0:
                val -= 0.01
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            # Evade: maximize distance, but avoid getting boxed by low mobility.
            # Prefer moving along a chosen wall edge when possible.
            edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            wall_edge = (wall_pref and (ny == 0 or ny == h - 1)) or ((not wall_pref) and (nx == 0 or nx == w - 1))
            val = d + 0.45 * m - 0.8 * prox
            if edge:
                val += 0.1
            if wall_edge:
                val += 0.2
            if dx == 0 and dy == 0:
                val -= 0.02
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]