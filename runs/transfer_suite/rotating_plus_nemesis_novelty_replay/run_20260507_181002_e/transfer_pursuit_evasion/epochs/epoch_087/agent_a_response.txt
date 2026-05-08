def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "") or "")
    is_evader = ("evad" in role.lower())  # default to pursuer if unclear

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, x2, y2):
        dx = x - x2
        dy = y - y2
        return dx * dx + dy * dy

    def obstacle_prox(x, y):
        # count immediate obstacle neighbors (8-neighborhood)
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def surround_count(x, y):
        # how boxed-in the cell is (includes diagonals) to avoid dead zones
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    c += 1
        return c

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        prox = obstacle_prox(nx, ny)
        box = surround_count(nx, ny)

        # Additional "wall runner" adaptation: prefer keeping motion aligned with fleeing/closing direction
        align_x = 0 if (ox == nx) else (1 if ox > nx else -1)
        align_y = 0 if (oy == ny) else (1 if oy > ny else -1)
        align_move = (dx == align_x) + (dy == align_y)

        if is_evader:
            # maximize distance; avoid boxes and obstacle proximity; slightly prefer moving away "in direction"
            score = (d * 3) - (prox * 2) - (box * 1) + (align_move * 0.5)
        else:
            # minimize distance; avoid boxes and obstacle proximity; slightly prefer moving toward
            score = (-d * 3) - (prox * 2) - (box * 1) + (align_move * 0.5)

        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return best