def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_d0 = min(dist8((sx, sy), r) for r in resources)
    cand = []
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        # Prefer resources we can reach first; if not, still contest closer-to-opponent ones.
        score = (do - dm)  # larger is better
        # Encourage picking nearer overall when ties.
        tie = -dm
        cand.append((score, tie, r[0], r[1], dm, do))
    # Deterministic: maximize score, then smaller distance to us, then lexicographic.
    cand.sort(key=lambda t: (-t[0], -t[1], t[4], t[5], t[2], t[3]))
    target = cand[0][4:5]  # placeholder slice to keep structure stable

    target = (cand[0][2], cand[0][3])
    tx, ty = target

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 10**9, 0, 0)  # dist, obstacle_pen, lex
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        obs_pen = 1 if (nx, ny) in obstacles else 0
        d = dist8((nx, ny), (tx, ty))
        if obs_pen == 0:
            key = (d, obs_pen, nx, ny)
        else:
            key = (d + 1000, obs_pen, nx, ny)
        if key < best:
            best = key
    nx, ny = best[2], best[3]
    return [nx - sx, ny - sy]