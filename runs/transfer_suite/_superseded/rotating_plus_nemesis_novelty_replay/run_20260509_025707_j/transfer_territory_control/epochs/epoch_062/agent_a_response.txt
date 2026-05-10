def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_to_center(x, y):
        dx, dy = x - cx, y - cy
        return dx * dx + dy * dy

    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_set:
                    return True
        return False

    # Determine whether to pressure (if behind) or contest center (otherwise)
    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    pressure = myc < opc

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    # Choose deterministically by scoring resulting cell
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        if (nx, ny) in opp_set:
            score += 1200.0 if pressure else 900.0
            score += 30.0 - dist_to_center(nx, ny) * 0.5
        elif (nx, ny) in unclaimed:
            score += 180.0
            score += (250.0 - dist_to_center(nx, ny) * 1.2) * (1.15 if pressure else 1.0)
        elif (nx, ny) in self_set:
            score += 18.0
            score += (120.0 - dist_to_center(nx, ny) * 0.6)

        # Encourage blocking by moving toward center and staying near potential flips
        dcent = dist_to_center(nx, ny)
        score += (120.0 - dcent) * (1.0 if not pressure else 0.7)
        if adj_opp(nx, ny):
            score += 85.0 if pressure else 60.0

        # Slight preference for moves that reduce distance to opponent "front"
        if observation.get("opponent_territory"):
            ox, oy = observation["opponent_position"]
            score += -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) * (0.01 if not pressure else 0.02)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]