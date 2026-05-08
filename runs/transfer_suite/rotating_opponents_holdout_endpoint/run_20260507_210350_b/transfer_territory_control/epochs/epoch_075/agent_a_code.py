def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        x0, y0 = (w - 1) // 2, (h - 1) // 2
        resources = [(x0, y0)]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        # Prefer moving into closer resource; also avoid approaching opponent.
        best_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        return (-best_res) * 3 + dist_opp

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            sc = score(nx, ny)
            if sc > best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc = sc
                best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]