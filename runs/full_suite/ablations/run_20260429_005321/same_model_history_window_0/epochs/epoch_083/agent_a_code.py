def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y, tx, ty):
        dx = tx - x
        dy = ty - y
        return dx * dx + dy * dy

    # If no resources, head toward opponent's corner to potentially contest.
    if not resources:
        tx, ty = (w - 1, h - 1) if (sx, sy) == (0, 0) else (0, 0)
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = dist2(sx, sy, rx, ry)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1] if best else (w - 1, h - 1)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            # Higher priority: move closer to target; slight bias to move off-grid? (none)
            d = dist2(nx, ny, tx, ty)
            # Small deterministic tie-breakers: avoid standing if possible, then prefer diagonals
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            diag_bonus = 0 if (dx == 0 or dy == 0) else -0.01
            # If opponent is closer to target, mildly prefer alternative paths (soft contention)
            opp_d = dist2(ox, oy, tx, ty)
            my_adv = (d - dist2(sx, sy, tx, ty)) + 0.0001 * stay_pen
            score = d + 2.0 * stay_pen + diag_bonus + 0.1 * (opp_d < d) - 0.0001 * my_adv
            candidates.append((score, stay_pen, dx, dy))

    # Always return something valid (stay put if all blocked).
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]