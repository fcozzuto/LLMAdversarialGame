def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs_list = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obs_list)
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neigh_count(nx, ny):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if not inb(ax, ay) or (ax, ay) in obs:
                    continue
                if (ax, ay) in unclaimed or (ax, ay) in opp:
                    c += 1
        return c

    # Opponent centroid (deterministic)
    if opp:
        ocx = sum(px for px, _ in opp) / float(len(opp))
        ocy = sum(py for _, py in opp) / float(len(opp))
    else:
        ocx, ocy = (w - 1) / 2.0, (h - 1) / 2.0

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        s = 0.0
        if (nx, ny) in unclaimed:
            s += 2.3
        elif (nx, ny) in opp:
            s += 1.8
        elif (nx, ny) in selft:
            s += 0.25
        else:
            s += 0.4

        # Frontier pressure: move near opponent/unclaimed
        s += 0.12 * neigh_count(nx, ny)

        # Prefer outward expansion from our territory
        if (x, y) in selft:
            if (nx, ny) not in selft:
                s += 1.0
            else:
                s -= 0.05

        # Mild attraction toward opponent
        dist = abs(nx - ocx) + abs(ny - ocy)
        s += -0.01 * dist

        # Slight penalty for staying put (encourage exploration)
        if dx == 0 and dy == 0:
            s -= 0.15

        if s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score = s
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]