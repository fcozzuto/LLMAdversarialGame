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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    if not resources:
        # No resources known: stay or slight maneuver toward center
        dx, dy = 0, 0
        if 0 <= mx+1 < w and (mx+1, my) not in obstacles:
            dx = 1
        elif 0 <= mx-1 < w and (mx-1, my) not in obstacles:
            dx = -1
        if 0 <= my+1 < h and (mx, my+1) not in obstacles:
            dy = 1
        elif 0 <= my-1 < h and (mx, my-1) not in obstacles:
            dy = -1
        return [dx, dy]

    # target nearest resource
    target = min(resources, key=lambda p: cheb((mx, my), p))

    # deterministically choose move: approach target while not stepping into obstacle.
    best = [0, 0]
    bestd = 9999
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny):
            continue
        d = cheb((nx, ny), target)
        # also consider distance to opponent to avoid direct capture risk
        od = cheb((nx, ny), (ox, oy))
        score = d*2 - od  # bias toward reaching resource while staying relatively safe
        if score < bestd:
            bestd = score
            best = [dx, dy]

    return best