def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    resources = []
    for p in observation.get("resources") or []:
        try:
            resources.append((p[0], p[1]))
        except Exception:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return (ax - bx if ax >= bx else bx - ax) + (ay - by if ay >= by else by - ay)

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            score = (man(nx, ny, tx, ty), nx, ny)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    opp_best = min((man(ox, oy, rx, ry) for rx, ry in resources), default=10**9)

    best = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        my_best = min((man(nx, ny, rx, ry) for rx, ry in resources), default=10**9)
        advantage = opp_best - my_best
        score = (-advantage, my_best, nx, ny)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]