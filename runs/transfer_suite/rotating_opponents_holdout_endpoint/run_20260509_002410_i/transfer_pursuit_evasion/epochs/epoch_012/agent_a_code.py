def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = observation.get("self_role", "") or ""
    evading = ("evad" in self_role.lower())

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    ti = int(observation.get("turn_index", 0) or 0)
    phase_corner = corners[ti % 4]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    target = far_corner if evading else phase_corner

    def adj_block_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                    c += 1
        return c

    best = None
    # fixed move order for determinism: prefer diagonals then straight then stay, with consistent tie-break
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        dist_to_target = abs(nx - target[0]) + abs(ny - target[1])
        block_pen = adj_block_count(nx, ny)

        # if evading, maximize distance from pursuer; also try to keep moving toward a far corner
        # if pursuing, minimize distance to opponent; also bias toward target corner to cut off routes
        if evading:
            primary = dist_to_opp
            secondary = dist_to_target
            # penalize closeness to obstacles (avoid getting cornered)
            score = (primary, secondary, -block_pen)
        else:
            primary = -dist_to_opp
            secondary = -dist_to_target
            score = (primary, secondary, -block_pen)

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]