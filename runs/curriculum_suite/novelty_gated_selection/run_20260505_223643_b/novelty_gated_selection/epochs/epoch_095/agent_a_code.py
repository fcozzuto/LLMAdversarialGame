def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # retreat-ish: increase distance from opponent while staying mobile
        best = (-(10**9), 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            oppd = dist((nx, ny), (ox, oy))
            mydedge = 0
            if nx == 0 or nx == w - 1: mydedge -= 1
            if ny == 0 or ny == h - 1: mydedge -= 1
            score = oppd + mydedge
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # pick a target resource that I can reach relatively better than opponent
    target = None
    best_key = None
    for r in resources:
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        key = (opd - myd, -myd, r[0], r[1])  # maximize lead, then closer, deterministic tie
        if best_key is None or key > best_key:
            best_key = key
            target = r

    tx, ty = target
    my_pos = (sx, sy)

    best = (-(10**9), 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        lead = opd - myd  # higher means I'm still ahead
        opp_dist_after = dist((nx, ny), (ox, oy))
        # discourage oscillation toward opponent; also avoid being stuck near edges
        edge_pen = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
        score = (lead * 3) - myd + (opp_dist_after * 0.2) - edge_pen * 0.1
        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]