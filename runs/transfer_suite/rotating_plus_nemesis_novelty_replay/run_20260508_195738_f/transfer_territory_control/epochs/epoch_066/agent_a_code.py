def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Build a small deterministic frontier sample: cells adjacent to opponent territory
    frontier = set()
    if opp:
        for px, py in opp:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    ax, ay = px + dx, py + dy
                    if inb(ax, ay) and (ax, ay) not in obs:
                        frontier.add((ax, ay))
    # Fallback targets: nearest unclaimed
    opp_list = list(opp)
    best_move = [0, 0]
    best_h = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        h = 0
        if (nx, ny) in opp:
            h += 200  # flip on entry
        if (nx, ny) in unclaimed:
            h += 80
        if opp:
            # adjacency pressure
            adj = 0
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    if (nx + ddx, ny + ddy) in opp:
                        adj = 1
                        break
                if adj:
                    break
            if adj:
                h += 35

            # Move towards frontier/opp (deterministic: min manhattan)
            if frontier and (nx, ny) in frontier:
                h += 25
            if opp_list:
                d = min(abs(px - nx) + abs(py - ny) for px, py in opp_list)
                h += (30 - min(30, d))  # higher when closer
        else:
            # No visible opponent territory: expand to unclaimed
            if unclaimed:
                d = min(abs(tx - nx) + abs(ty - ny) for tx, ty in unclaimed)
                h += (50 - min(50, d))
            else:
                h += -abs(nx - (w // 2)) - abs(ny - (h // 2))

        # Mild preference for not staying still if there's any capturing/expansion move
        if dx == 0 and dy == 0:
            h -= 3

        if h > best_h:
            best_h = h
            best_move = [dx, dy]

    return best_move