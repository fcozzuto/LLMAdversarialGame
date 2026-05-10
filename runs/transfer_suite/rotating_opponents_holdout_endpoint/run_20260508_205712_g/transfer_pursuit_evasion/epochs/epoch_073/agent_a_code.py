def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    sr = str(observation.get("self_role") or "").lower()
    is_evader = not (("pursuer" in sr) or ("pred" in sr) or ("catch" in sr) or ("hunter" in sr))

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer moves that (for pursuer) approach, (for evader) run away, while avoiding obstacles.
    # Secondary heuristic: bias toward center for evader, toward opponent for pursuer.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if is_evader:
            dist_score = d2
            center_score = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            # Also discourage heading into the nearest opponent line when roles are ambiguous.
            val = dist_score + 0.05 * center_score
        else:
            dist_score = -d2
            center_score = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            val = dist_score + 0.01 * center_score

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]