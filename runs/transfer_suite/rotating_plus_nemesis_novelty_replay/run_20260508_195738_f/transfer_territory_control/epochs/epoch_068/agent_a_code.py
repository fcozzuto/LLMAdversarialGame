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
    parity = int(observation.get("turn_index", 0)) & 1

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neigh_has_opp(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in opp:
                    return True
        return False

    opp_list = list(opp) if opp else None
    def nearest_opp_dist(nx, ny):
        if not opp_list:
            return 10**9
        dmin = 10**9
        for px, py in opp_list:
            d = abs(px - nx) + abs(py - ny)
            if d < dmin:
                dmin = d
        return dmin

    # Move scoring: prioritize claiming unclaimed, then threatening opponent, then expanding.
    best = None
    best_moves = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 120
        if (nx, ny) in selft:
            score += 20
        if (nx, ny) in opp:
            score += 60  # flipping on entry
        if neigh_has_opp(nx, ny):
            score += 45
        d = nearest_opp_dist(nx, ny)
        if opp_list:
            score += max(0, 30 - 6 * d)
        # mild center/alt bias to reduce stagnation
        score += -2 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        # deterministic tie-break with parity
        score += ((nx + 3 * ny + parity) % 2) * 0.01

        if best is None or score > best:
            best = score
            best_moves = [(dx, dy)]
        elif score == best:
            best_moves.append((dx, dy))

    if not best_moves:
        return [0, 0]
    # Deterministic choose among equals
    best_moves.sort(key=lambda m: (m[0], m[1]))
    return list(best_moves[parity % len(best_moves)])