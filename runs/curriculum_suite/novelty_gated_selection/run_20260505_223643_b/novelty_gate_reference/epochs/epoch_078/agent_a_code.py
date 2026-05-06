def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best_move = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # pick the resource that looks best from (nx,ny) with "race" logic
        best_r = None
        best_r_key = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer resources we can reach no later; otherwise minimize how far behind we are.
            if sd <= od:
                r_key = (0, sd, sd - od, rx, ry)
            else:
                r_key = (1, sd - od, sd, rx, ry)
            if best_r_key is None or r_key < best_r_key:
                best_r_key = r_key
                best_r = (rx, ry)

        rx, ry = best_r
        sd = md(nx, ny, rx, ry)
        od = md(ox, oy, rx, ry)

        # Extra pressure: if we are behind, try to increase opponent distance while still advancing.
        opp_dist = md(nx, ny, ox, oy)
        if sd <= od:
            m_key = (0, sd, od - sd, -opp_dist, rx, ry)
        else:
            m_key = (1, sd - od, sd, -opp_dist, rx, ry)

        if best_key is None or m_key < best_key:
            best_key = m_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]