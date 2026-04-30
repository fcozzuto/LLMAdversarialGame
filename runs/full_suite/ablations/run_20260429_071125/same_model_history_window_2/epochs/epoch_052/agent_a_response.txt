def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Determine opponent pressure: resources where opponent is closer than us.
    opp_pressure = []
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if opd < myd:
            opp_pressure.append((opd - myd, rx, ry))  # negative means opponent is closer
    opp_pressure.sort()
    pressured = opp_pressure[0][1:] if opp_pressure else None

    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in valid:
        # Evaluate by best "steal" opportunity after moving.
        # Primary: maximize distance advantage (opp - me); Secondary: get closer to a pressured resource if exists.
        steal = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            val = (opd - myd) * 10 - myd  # prefer taking/contesting sooner
            if val > steal:
                steal = val
        if pressured is not None:
            rx, ry = pressured
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            steal = steal + (opd - myd) * 6 - myd  # bias toward contesting what opp already leads
        # Small tie-break: move toward center to reduce cornering risk.
        center_boost = -(abs((nx * 2 + 1) - w) + abs((ny * 2 + 1) - h))
        val = steal + center_boost

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]