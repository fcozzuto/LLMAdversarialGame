def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    i_am_pursuer = (("pursuer" in srole) or ("chaser" in srole) or ("catch" in srole) or ("pursuit" in srole))
    if "evader" in srole or "evad" in srole:
        i_am_pursuer = False
    if (("pursuer" in orole) or ("chaser" in orole) or ("catch" in orole) or ("pursuit" in orole)):
        i_am_pursuer = False

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for ddx, ddy in dirs:
            if free(x + ddx, y + ddy):
                c += 1
        return c

    # Deterministic tie-breaker preference order: center then toward increasing x then increasing y
    def score_for_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        m = mobility(nx, ny)
        d = dist2(nx, ny)
        # pursuer: minimize distance, then maximize mobility
        if i_am_pursuer:
            return (d, -m, -abs(dx), -abs(dy), -dx, -dy)
        # evader: maximize distance, then maximize mobility (stay evasive)
        return (-d, -m, -abs(dx), -abs(dy), -dx, -dy)

    best_move = None
    best_score = None
    for dx, dy in moves:
        sc = score_for_move(dx, dy)
        if best_score is None or sc < best_score:
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]