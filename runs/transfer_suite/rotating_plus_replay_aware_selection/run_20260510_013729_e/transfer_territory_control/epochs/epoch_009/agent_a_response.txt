def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    resources = set(map(tuple, observation.get("resources", [])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_score(nx, ny):
        sc = 0
        if (nx, ny) in resources:
            sc += 35
        if (nx, ny) in unclaimed:
            sc += 55
        if (nx, ny) in self_ter:
            sc += 6
        if (nx, ny) in opp_ter:
            sc -= 140

        # Encourage expansion while not stepping into opponent territory
        dist_opp = abs(nx - ox) + abs(ny - oy)
        sc += max(0, 20 - dist_opp) * (2 if (nx, ny) not in opp_ter else -3)

        # Prefer moving toward the global nearest unclaimed cell (if any)
        if unclaimed:
            # simple deterministic estimate: use a few candidate unclaimed based on ordering
            # (avoid heavy search; list iteration is deterministic)
            best_d = 10**9
            cnt = 0
            for ux, uy in unclaimed:
                d = abs(ux - nx) + abs(uy - ny)
                if d < best_d:
                    best_d = d
                cnt += 1
                if cnt >= 10:
                    break
            if best_d < 10**9:
                sc += max(0, 18 - best_d) * 2

        # Discourage getting boxed-in by obstacles
        neigh_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty) or (tx, ty) in obstacles:
                neigh_obs += 1
        sc -= neigh_obs * 4

        return sc

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = cell_score(nx, ny)
        # Deterministic tie-break: prefer larger dx, then larger dy (stable for equal sc)
        if sc > best_sc or (sc == best_sc and (dx, dy) > (best[0], best[1])):
            best_sc = sc
            best = [dx, dy]

    return best