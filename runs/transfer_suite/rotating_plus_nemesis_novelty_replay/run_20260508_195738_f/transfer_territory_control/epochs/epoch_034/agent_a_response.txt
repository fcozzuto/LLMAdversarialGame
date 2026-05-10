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

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = (-10**18, 0, 0)
    un_list = list(unclaimed)  # small; deterministic fallback

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0.0
        if (nx, ny) in opp:
            score += 5.0  # flipping opponent control on entry
        elif (nx, ny) in unclaimed:
            score += 2.0  # claim new space
        elif (nx, ny) in selft:
            score += 0.5  # consolidation

        # Prefer moving toward opponent edge / frontier near our territory
        edge = 0
        for adx, ady in neigh4:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay):
                if (ax, ay) in opp:
                    edge += 1
                elif (ax, ay) in unclaimed:
                    edge += 0.5
                elif (ax, ay) in selft:
                    edge += 0.25
        score += edge * 0.75

        # Deterministic tie-break: push toward nearest unclaimed if any exist
        if un_list:
            dmin = 10**9
            for ux, uy in un_list[:]:  # deterministic order from observation
                d = abs(ux - nx) + abs(uy - ny)
                if d < dmin:
                    dmin = d
            score += -0.08 * dmin

        if score > best[0] or (score == best[0] and (dx, dy) != (best[1], best[2]) and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    if best[1] == 0 and best[2] == 0:
        # if no move chosen (blocked), stay
        return [0, 0]
    return [int(best[1]), int(best[2])]