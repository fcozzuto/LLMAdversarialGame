def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obst

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            key = (man(nx, ny, cx, cy), abs(nx - ox) + abs(ny - oy))
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best_move = None
    best_score = None

    # Prefers securing a resource where we are strictly closer than opponent,
    # otherwise still advances toward the best available resource while avoiding "handoffs".
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Diagonal probe mitigation: keep moving away from opponent's diagonal line to reduce direct pursuit overlap
        diag_line_pen = 0
        if (sx - sy) == (ox - oy):
            diag_line_pen = 1
        if (nx - ny) == (ox - oy):
            diag_line_pen = 2

        best_cell = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # Win pressure: prioritize resources we can reach before opponent.
            # If opponent can tie/beat us, penalize heavily (prevents "opportunistic handoffs").
            tie_pen = 0
            if opp_d <= self_d:
                tie_pen = 200 + (self_d - opp_d)  # large, deterministic

            # Also prefer shorter paths and some center-leaning.
            center_bias = 0.01 * man(nx, ny, cx, cy)
            gain = (opp_d - self_d)
            score = gain * 10 - self_d - tie_pen - diag_line_pen + center_bias

            if best_cell is None or score > best_cell[0]:
                best_cell = (score, (rx, ry))

        if best_cell is None:
            continue

        if best_score is None or best_cell[0] > best_score:
            best_score = best_cell[0]
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]