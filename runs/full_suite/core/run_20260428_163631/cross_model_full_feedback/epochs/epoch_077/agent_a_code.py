def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_close = man(sx, sy, ox, oy)
    best = None
    for dx, dy, nx, ny in legal:
        if resources:
            my_best = 10**9
            opp_best = 10**9
            for rx, ry in resources:
                my_best = min(my_best, man(nx, ny, rx, ry))
                opp_best = min(opp_best, man(ox, oy, rx, ry))
            # Prefer moving closer than opponent; boost capturing if already on a resource.
            on_res = 1 if (nx, ny) in set(resources) else 0
            score = (on_res * 1000000) + (opp_best - my_best) * 1000 - my_best
        else:
            score = 0
        # Avoid getting too close to opponent unless very close to a resource.
        dno = man(nx, ny, ox, oy)
        score -= max(0, 4 - dno) * (100 if resources else 30)
        key = (-score, dx, dy)  # deterministic tie-break
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]