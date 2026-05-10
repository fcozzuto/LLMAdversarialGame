def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_dist_to_cells(x, y, cells):
        if not cells:
            return 10**9
        best = 10**9
        cap = 32 if len(cells) > 32 else len(cells)
        for i in range(cap):
            cx, cy = cells[i]
            d = abs(cx - x) + abs(cy - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best if best != 10**9 else 10**9

    up = observation.get("self_territory_count", 0)
    op = observation.get("opponent_territory_count", 0)
    we_lead = up >= op

    target_cells = unclaimed if unclaimed else []
    nearest_unclaimed = unclaimed if unclaimed else []
    nearest_op_cells = list(op_terr) if op_terr else []

    best = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Immediate reward for taking/claiming
        cell_unclaimed = (nx, ny) in set(target_cells[:64]) if target_cells else False
        cell_self = (nx, ny) in self_terr
        cell_op = (nx, ny) in op_terr

        d_unclaimed = best_dist_to_cells(nx, ny, nearest_unclaimed) if nearest_unclaimed else 0
        d_op = best_dist_to_cells(nx, ny, nearest_op_cells) if nearest_op_cells else 10**9

        # Heuristic: advance toward nearest unclaimed; if we trail, allow contesting opponent territory more.
        score = 0
        score += 3 if cell_unclaimed else 0
        score += 1 if cell_self else 0
        if cell_op:
            score += 2 if not we_lead else -1  # flip is good if behind, avoid if ahead
        score += 0.5 * (1.0 / (1 + d_op)) if nearest_op_cells else 0

        # Prefer smaller distance to unclaimed frontier
        score -= 0.25 * d_unclaimed

        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]