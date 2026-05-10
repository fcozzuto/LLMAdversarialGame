def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    opp_count = int(observation.get("opponent_territory_count", len(opp_t)))
    self_count = int(observation.get("self_territory_count", len(self_t)))
    center_pressure = 1.0 if opp_count > self_count else 0.0

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in opp_t:
            score += 8.0
        elif (nx, ny) in unclaimed:
            score += 5.0
        elif (nx, ny) in self_t:
            score += 1.0
        else:
            score += 2.0

        d_to_opp = manhattan(nx, ny, ox, oy)
        d_to_center = abs(nx - cx) + abs(ny - cy)

        score += 0.07 * d_to_opp
        if center_pressure >= 0.5:
            score += -0.03 * d_to_center  # contest center less when behind
        else:
            score += -0.05 * d_to_center  # expand toward center when ahead

        # Deterministic tie-breaker: favor moves that improve Manhattan distance from opponent,
        # then prefer a stable ordering with parity.
        score += (0.001 if ((observation.get("turn_index", 0) % 2) == 0) else -0.001) * (dx * 2 + dy)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            if (d_to_opp > manhattan(best_move[0] + sx, best_move[1] + sy, ox, oy)):
                best_move = [dx, dy]

    if best_move == [0, 0] and ((sx, sy) not in obstacles):
        return [0, 0]
    return best_move if best_move else [0, 0]