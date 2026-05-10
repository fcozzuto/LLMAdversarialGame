def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Prefer moving so that we become (or stay) closer than opponent to some resource,
    # while avoiding obstacles and selecting a strong target deterministically.
    best_move = [0, 0]
    best_score = None

    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue

        self_best_margin = -10**9
        self_best_res_d = 10**9

        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd  # positive means we are closer (or equal)
            # Secondary: prioritize smaller distance for likely collection.
            if margin > self_best_margin or (margin == self_best_margin and sd < self_best_res_d):
                self_best_margin = margin
                self_best_res_d = sd

        # Also consider immediate progress to the globally nearest resource.
        nearest_now = min(resources, key=lambda r: cheb(nx, ny, r[0], r[1]))[0:2]
        prog = cheb(sx, sy, nearest_now[0], nearest_now[1]) - cheb(nx, ny, nearest_now[0], nearest_now[1])

        # Coefficients tuned deterministically for stronger stealing over pure chasing.
        score = (self_best_margin * 1000) + (prog * 10) + (-self_best_res_d)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [mx, my]

    return best_move