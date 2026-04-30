def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_dx, best_dy = 0, 0
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if not resources:
            val = manhattan(nx, ny, ox, oy)  # deterministic fallback
        else:
            # Choose the resource that gives best relative advantage, evaluated from next position
            best_for_move = None
            for rx, ry in resources:
                ds = manhattan(nx, ny, rx, ry)
                do = manhattan(ox, oy, rx, ry)
                # Higher is better: prefer smaller ds and larger (do - ds)
                val = (do - ds) * 1000 - ds
                if best_for_move is None or val > best_for_move:
                    best_for_move = val
            val = best_for_move
        if best_val is None or val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy
        elif val == best_val:
            if (dx, dy) < (best_dx, best_dy):
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]