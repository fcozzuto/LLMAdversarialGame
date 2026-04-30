def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x0, y0 = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obst = set((p[0], p[1]) for p in obstacles)
    res = set((p[0], p[1]) for p in resources)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if res:
        target = None
        best = None
        for rx, ry in res:
            sd = d2(x0, y0, rx, ry)
            od = d2(ox, oy, rx, ry)
            score = sd - 0.6 * od
            if best is None or score < best:
                best = score
                target = (rx, ry)
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    opp_next = set()
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            opp_next.add((nx, ny))

    best_move = (0, 0)
    best_val = None
    tr, tc = target
    for dx, dy in deltas:
        nx, ny = x0 + dx, y0 + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        danger = 1.0 if (nx, ny) in opp_next else 0.0
        move_to_resource = 1.0 if (nx, ny) in res else 0.0
        v = 0.0
        v += -1000.0 * danger
        v += 200.0 * move_to_resource
        v += -d2(nx, ny, tr, tc)  # closer to target is better
        # slight preference to keep distance from opponent while advancing
        v += 0.1 * d2(nx, ny, ox, oy)
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]