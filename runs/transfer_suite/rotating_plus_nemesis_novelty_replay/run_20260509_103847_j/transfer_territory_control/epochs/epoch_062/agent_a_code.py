def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unT = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.append((x, y))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opT.add((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def best_target():
        if not unT:
            return None
        # Prefer quick claims near center while reducing how close we stay to opponent control fronts.
        # Tie-break deterministically by lexicographic (x,y).
        best = None
        best_val = None
        for (x, y) in unT:
            d_self = abs(x - sx) + abs(y - sy)
            d_op = abs(x - ox) + abs(y - oy)
            near_op = 1 if (x, y) in opT else 0
            center_bias = abs(x - cx) + abs(y - cy)
            # Lower is better
            val = (0.9 * d_self) + (0.15 * center_bias) - (0.55 * d_op) - (2.2 * near_op)
            if best_val is None or val < best_val or (val == best_val and (x, y) < best):
                best_val = val
                best = (x, y)
        return best

    target = best_target()
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if target is None:
        # Fallback: go toward center while staying off obstacles
        tx, ty = cx, cy
    else:
        tx, ty = target

    # Choose deterministic move that reduces distance to target and avoids obstacles
    best_move = (0, 0)
    best_dist = None
    best_hits = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        hit = 1 if (nx, ny) in obstacles else 0
        if hit:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        # tie-break: prefer keeping diagonals/axes (lexicographic) deterministically
        key = (dist, hit, dx, dy)
        if best_dist is None or key < (best_dist, best_hits, best_move[0], best_move[1]):
            best_dist = dist
            best_hits = hit
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]