def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = isinstance(ox, (int, float)) and isinstance(oy, (int, float))
    ox = int(ox) if opp_exists else 0
    oy = int(oy) if opp_exists else 0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if not resources:
            val = -(abs(nx - (w - 1)) + abs(ny - (h - 1)))
        else:
            best = -10**18
            for rx, ry in resources:
                sd = abs(nx - rx) + abs(ny - ry)
                if opp_exists:
                    od = abs(ox - rx) + abs(oy - ry)
                    margin = od - sd
                    cand = 5 * margin - sd
                else:
                    cand = -sd
                if cand > best:
                    best = cand
            val = best
            # Small bias to prevent oscillation: prefer moves that don't increase distance to the chosen best resource too much
            if opp_exists and resources:
                val -= 0.01 * (abs((sx + dx) - ox) + abs((sy + dy) - oy))
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]