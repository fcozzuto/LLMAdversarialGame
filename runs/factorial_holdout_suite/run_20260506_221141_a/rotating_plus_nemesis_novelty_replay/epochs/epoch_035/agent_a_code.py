def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < gw and 0 <= y < gh:
                obs.add((x, y))
    cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obs:
                cells.append((x, y))
    if not cells:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_move = (0, 0)
    best_key = (-10**18, -10**18, -10**18)
    for dx, dy, nx, ny in moves:
        best_gap = -10**18
        best_sd = 10**18
        best_rd = None
        for rx, ry in cells:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd
            if gap > best_gap or (gap == best_gap and sd < best_sd):
                best_gap = gap
                best_sd = sd
                best_rd = (rx, ry)
        rx, ry = best_rd
        # Add slight preference to move toward the chosen resource more directly.
        direct = abs(rx - nx) + abs(ry - ny)
        key = (best_gap, -best_sd, -direct)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]