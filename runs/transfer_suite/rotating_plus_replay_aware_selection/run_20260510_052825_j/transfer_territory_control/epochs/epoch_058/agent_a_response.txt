def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not unclaimed and not oppT:
        return [0, 0]

    # Choose a primary target deterministically: closest unclaimed, else closest opp territory
    def dist2(p):
        return (p[0] - x) * (p[0] - x) + (p[1] - y) * (p[1] - y)

    if unclaimed:
        target = min(unclaimed, key=lambda p: (dist2(p), p[1], p[0]))
        mode = "unclaimed"
    else:
        target = min(oppT, key=lambda p: (dist2(p), p[1], p[0]))
        mode = "opp"

    best_move = (0, 0)
    best_score = -10**18

    # Local neighborhood bonus to keep expansion/frontier
    neigh_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0

        if (nx, ny) in unclaimed:
            score += 8.0 if mode == "unclaimed" else 5.0
        elif (nx, ny) in oppT:
            score += 4.5 if mode != "unclaimed" else 3.0
        elif (nx, ny) in selfT:
            score += 1.5
        else:
            score += 0.3

        # Move closer to target
        score += 1.8 * (dist2(target) - ((nx - target[0]) * (nx - target[0]) + (ny - target[1]) * (ny - target[1])))

        # Frontier pressure: prefer moves adjacent to unclaimed/opp
        adj = 0
        for ax, ay in neigh_dirs:
            xx, yy = nx + ax, ny + ay
            if 0 <= xx < w and 0 <= yy < h:
                if (xx, yy) in unclaimed:
                    adj += 2
                elif (xx, yy) in oppT:
                    adj += 1
        score += adj * 0.7

        # Mild bias to avoid getting stuck near center loop by preferring non-stay if tie
        if dx == 0 and dy == 0:
            score -= 0.05

        # Deterministic tie-break: earlier in deltas list wins
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]