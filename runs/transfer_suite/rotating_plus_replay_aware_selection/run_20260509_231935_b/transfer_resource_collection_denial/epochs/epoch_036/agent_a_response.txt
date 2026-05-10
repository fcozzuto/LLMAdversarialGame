def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources_list = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    res = set((p[0], p[1]) for p in resources_list)
    obs = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Immediate pickup
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            return [dx, dy]

    if not resources_list:
        return [0, 0]

    # Choose best target resource by "who gets there first"
    best_t = None
    best_tv = None
    for rx, ry in res:
        if (rx, ry) in obs:
            continue
        sd = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; tie-break toward closer overall
        tv = (od - sd, -(sd + 0.01 * (rx + 3 * ry)))
        if best_tv is None or tv > best_tv:
            best_tv = tv
            best_t = (rx, ry)

    rx, ry = best_t
    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in res:
            return [dx, dy]

        # Greedy toward target plus slight pressure to deny opponent paths
        sd2 = dist8(nx, ny, rx, ry)
        od2 = dist8(ox, oy, rx, ry)
        lead = od2 - sd2
        # Secondary: keep moving (avoid idle) and reduce distance traveled in key areas
        idle_pen = -1 if (dx == 0 and dy == 0) else 0
        opp_keep = -0.001 * dist8(nx, ny, ox, oy)
        key = (lead, -sd2, idle_pen, opp_keep)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]