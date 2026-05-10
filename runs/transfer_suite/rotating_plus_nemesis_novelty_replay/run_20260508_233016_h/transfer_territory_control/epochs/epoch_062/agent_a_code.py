def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    resources = set(tuple(p) for p in (observation.get("resources") or []))
    rem = observation.get("remaining_resource_count", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    tx = ty = None
    if unclaimed:
        best = None
        for x, y in unclaimed:
            if not inb(x, y):
                continue
            if (x, y) in obstacles:
                continue
            d1 = abs(x - sx) + abs(y - sy)
            d2 = abs(x - ox) + abs(y - oy)
            score = d1 + 0.3 * d2
            if (x, y) in oppT:
                score += 5
            if best is None or score < best[0]:
                best = (score, x, y)
        tx, ty = best[1], best[2]
    elif resources and rem:
        best = None
        for x, y in resources:
            if not inb(x, y) or (x, y) in obstacles:
                continue
            score = abs(x - sx) + abs(y - sy)
            if best is None or score < best[0]:
                best = (score, x, y)
        tx, ty = best[1], best[2]
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in selfT:
            val = 10000
        else:
            val = 0
            if (nx, ny) in oppT:
                val += 20
            val += abs(nx - tx) + abs(ny - ty)
            if unclaimed and (nx, ny) in set(tuple(p) for p in unclaimed[:200]):
                val -= 5
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]