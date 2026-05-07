def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, dict):
            x = p.get("x", None); y = p.get("y", None)
            if x is not None and y is not None:
                obstacles.add((int(x), int(y)))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, dict):
            x = r.get("x", None); y = r.get("y", None)
            if x is not None and y is not None:
                resources.append((int(x), int(y)))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        return [0, 0]

    res_set = set(resources)

    def clamp_inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    def closest_dist(px, py):
        best = None
        for (rx, ry) in resources:
            d = md(px, py, rx, ry)
            if best is None or d < best:
                best = d
        return best if best is not None else 10**9

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    self_closest_now = closest_dist(sx, sy)
    opp_closest_now = closest_dist(ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_inb(nx, ny) or (nx, ny) in obstacles:
            continue

        self_closest = closest_dist(nx, ny)
        opp_closest = opp_closest_now

        adv = opp_closest - self_closest  # higher is better
        collect_bonus = 0
        if (nx, ny) in res_set:
            collect_bonus = 1000 - self_closest  # strong immediate priority

        # Secondary: if both are similar, prefer reducing own distance and avoid stepping too far from current progress
        score = (adv + collect_bonus, -self_closest, -(abs(nx - sx) + abs(ny - sy)), -self_closest_now)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]