def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    target = None
    if resources:
        target = min(resources, key=lambda p: cheb((mx, my), p))

    best_dxdy = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        score = 0
        if target is not None:
            score -= cheb((nx, ny), target) * 2  # bias toward reaching resource
        # discourage stepping onto opponent or too close if it increases danger
        dist_opp = cheb((nx, ny), (ox, oy))
        if dist_opp == 0:
            score -= 5
        elif dist_opp == 1:
            score -= 1
        # simple attraction to center to avoid edges if resources scarce
        center_x, center_y = w//2, h//2
        score -= cheb((nx, ny), (center_x, center_y)) * 0.1

        if score > best_score:
            best_score = score
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]