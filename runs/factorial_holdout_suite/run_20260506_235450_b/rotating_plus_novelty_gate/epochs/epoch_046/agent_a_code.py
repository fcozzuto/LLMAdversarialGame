def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_val = -10**18

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    def pick_val(nx, ny):
        immediate = 0
        best = -10**18
        for i in range(len(resources)):
            rx, ry = resources[i]
            s_d = dist(nx, ny, rx, ry)
            o_d = dist(ox, oy, rx, ry)
            adv = (o_d - s_d)  # positive means we are closer than opponent
            if s_d == 0:
                immediate = 1
                score = 10**7 + adv * 1000 - s_d
            else:
                # Strongly prefer taking resources we can beat the opponent on.
                score = adv * 5000 - s_d * 20
                # Small bias toward lower index to break ties deterministically.
                score -= i * 0.001
            if score > best:
                best = score
        return best + (10**6 if immediate else 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        val = pick_val(nx, ny)
        if val > best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]