def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid_resources = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid_resources.append((x, y))
    if not valid_resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep us in place on invalid move

        best_lead = None
        best_time = None
        best_our_dist = None
        for rx, ry in valid_resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            if best_lead is None or lead > best_lead or (lead == best_lead and (ds < best_time or best_time is None)):
                best_lead = lead
                best_time = ds
                best_our_dist = ds

        # Secondary tie-break: prioritize smaller our distance to the best-leading resource;
        # then slightly prefer moving toward the board center to reduce pathing loops.
        center_x = (w - 1) / 2.0
        center_y = (h - 1) / 2.0
        center_pref = -((nx - center_x) * (nx - center_x) + (ny - center_y) * (ny - center_y))

        score = (best_lead, -int(best_our_dist if best_our_dist is not None else 10**9), center_pref, -cheb(nx, ny, ox, oy))
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)

    return [int(best_move[1]), int(best_move[2])]