def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def cells_from(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    selfT = cells_from("self_territory")
    opT = cells_from("opponent_territory")

    resources = cells_from("resources")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_op = abs(nx - ox)
        e_op = abs(ny - oy)
        dist = d_op if d_op > e_op else e_op  # Chebyshev
        sc = dist * 3
        if (nx, ny) in resources:
            sc += 100
        if (nx, ny) in selfT:
            sc += 5
        if (nx, ny) in opT:
            sc -= 25
        if best is None or sc > best_score:
            best_score = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]