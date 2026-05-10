def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def score_cell(x, y):
        adj_un = 0
        adj_opp = 0
        adj_self = 0
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) in unclaimed:
                    adj_un += 1
                elif (nx, ny) in oppT:
                    adj_opp += 1
                elif (nx, ny) in selfT:
                    adj_self += 1
        in_un = 1.0 if (x, y) in unclaimed else 0.0
        in_opp = 1.0 if (x, y) in oppT else 0.0
        # Greedy expansion with a bias to flip nearby opponent cells; keep close to own territory.
        return (2.2 * in_un + 1.0 * in_opp) + 0.22 * adj_un + 0.35 * adj_opp - 0.10 * adj_self

    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)
        # Deterministic tie-break: prefer non-diagonal, then smaller abs dx, then lexicographic.
        key = (sc, -1 if dx == 0 or dy == 0 else 0, -abs(dx), -abs(dy), -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]