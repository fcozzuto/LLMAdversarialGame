def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    obs_cells = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_cells)
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    oppt = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))

    opp_list = list(oppt)
    if opp_list:
        cx = sum(px for px, _ in opp_list) / len(opp_list)
        cy = sum(py for _, py in opp_list) / len(opp_list)
    else:
        cx, cy = w - 1, h - 1

    def inb(a, b): return 0 <= a < w and 0 <= b < h
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)
    best_move = (0, 0)

    # Prefer capturing/expanding while keeping distance from obstacles via local safety.
    # Safety: penalize moves that have many blocked neighbor cells (including self step reverting).
    neigh = dirs

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0

        # Cell type
        if (nx, ny) in unclaimed:
            val += 4.0
        elif (nx, ny) in oppt:
            val += 8.0
        elif (nx, ny) in selft:
            val += 1.5
        else:
            val += 0.5  # other controlled/empty

        # Move toward opponent territory center (or toward where it is likely)
        dcur = abs(cx - x) + abs(cy - y)
        dnext = abs(cx - nx) + abs(cy - ny)
        val += (dcur - dnext) * 0.9

        # Encourage frontier expansion: adjacency to self
        adj_self = 0
        for ax, ay in neigh:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in selft:
                adj_self += 1
        val += adj_self * 0.35

        # If stepping into opponent, bias also by closeness to unclaimed next to them
        if (nx, ny) in oppt:
            # Look for nearby unclaimed cells to keep momentum
            near_un = 0
            for ax, ay in neigh:
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in unclaimed:
                    near_un += 1
            val += near_un * 0.7

        # Local safety: penalize being surrounded by obstacles
        blocked = 0
        for ax, ay in neigh:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty) or (tx, ty) in obstacles:
                blocked += 1
        val -= blocked * 0.06

        # Mild preference to avoid pointless oscillation: prefer staying only if no better
        if (dx, dy) == (0, 0):
            val -= 0.15

        # Deterministic tie-breaker by dir order index
        idx = dirs.index((dx, dy))
        cand = (val, -idx, nx * 9 + ny)
        if cand > best:
            best = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]