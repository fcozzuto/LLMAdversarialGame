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

    def adj_has_opp(nx, ny):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (nx + ddx, ny + ddy) in opp:
                    return True
        return False

    opp_list = list(opp)
    def nearest_opp_dist(nx, ny):
        if not opp_list:
            return 10**9
        dmin = 10**9
        for px, py in opp_list:
            d = abs(px - nx) + abs(py - ny)
            if d < dmin:
                dmin = d
        return dmin

    candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        score = 0.0
        if (nx, ny) in opp:
            score += 10.0
        if (nx, ny) in unclaimed:
            score += 3.0 if adj_has_opp(nx, ny) else 0.5
        if (nx, ny) in selft:
            score += 1.0 if (nx, ny) != (x, y) else 0.2
        if adj_has_opp(nx, ny):
            score += 1.2
        score -= 0.08 * nearest_opp_dist(nx, ny)
        # deterministic tie-breaker: prefer moves that reduce manhattan to nearest opp, then lexicographic
        candidates.append((score, abs(nx - x) + abs(ny - y), nearest_opp_dist(nx, ny), dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
    _, _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]