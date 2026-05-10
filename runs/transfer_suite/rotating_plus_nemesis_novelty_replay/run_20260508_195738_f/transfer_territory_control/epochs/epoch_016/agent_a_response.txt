def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_to_opp(px, py):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = px + dx, py + dy
                if (ax, ay) in opp:
                    return True
        return False

    opp_targets = []
    for cx, cy in unclaimed:
        if adj_to_opp(cx, cy):
            d = abs(cx - x) + abs(cy - y)
            opp_targets.append((d, cx, cy))
    opp_targets.sort()
    frontier = None
    if opp_targets:
        frontier = (opp_targets[0][1], opp_targets[0][2])

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        if (nx, ny) in opp:
            val += 5  # immediate flipping pressure
        if (nx, ny) in unclaimed:
            val += 3  # claim unclaimed quickly
        if (nx, ny) in selft:
            val += 1  # maintain control

        if frontier is not None:
            df = abs(frontier[0] - nx) + abs(frontier[1] - ny)
            d0 = abs(frontier[0] - x) + abs(frontier[1] - y)
            val += (d0 - df) * 0.5  # greedy progress to frontier

        if adj_to_opp(nx, ny):
            val += 1.5  # stay near sweep lines

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move