def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_val = -10**18
    best = [0, 0]

    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)

        val = 0
        if (nx, ny) in self_t:
            val += 3
        if (nx, ny) in unclaimed:
            val += 9
            val += max(0, 6 - d_opp) * 2
        if (nx, ny) in opp_t:
            val += 55
            val += max(0, 6 - d_opp) * 3

        # Prefer expanding away from immediate opponent pressure; avoid getting trapped near them.
        val += (d_opp - (abs(sx - ox) + abs(sy - oy))) * 1.2

        # Small deterministic tie-breaker to reduce oscillations.
        if dx == 0 and dy == 0:
            val -= 2
        if dx == 1 and dy == 0:
            val += 0.01
        elif dx == -1 and dy == 0:
            val += 0.00
        elif dx == 0 and dy == 1:
            val += 0.02
        elif dx == 0 and dy == -1:
            val += 0.03
        elif dx == 1 and dy == 1:
            val += 0.04
        elif dx == -1 and dy == 1:
            val += 0.05
        elif dx == 1 and dy == -1:
            val += 0.06
        elif dx == -1 and dy == -1:
            val += 0.07

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]