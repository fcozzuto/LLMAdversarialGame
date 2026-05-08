def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    selfT = set(tuple(p) for p in observation.get("self_territory", []))
    oppT = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                gain = 0
                if (nx, ny) in oppT:
                    gain = 3
                elif (nx, ny) in unclaimed:
                    gain = 2
                elif (nx, ny) in selfT:
                    gain = 0
                dist_center = abs(nx - cx) + abs(ny - cy)
                best_unclaimed_dist = 0
                if unclaimed:
                    best_unclaimed_dist = min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed)
                moves.append((gain, -dist_center, -best_unclaimed_dist, ny, nx, dx, dy))

    if moves:
        moves.sort(reverse=True)
        _, _, _, _, _, dx, dy = moves[0]
        return [dx, dy]

    return [0, 0]