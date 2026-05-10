def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def best_res_dist2(x, y):
        if not res:
            return None
        best = None
        for rx, ry in res:
            d = (x - rx) * (x - rx) + (y - ry) * (y - ry)
            if best is None or d < best:
                best = d
        return best

    sep0 = abs(sx - ox) + abs(sy - oy)
    role = str(observation.get("self_role", "")).lower()
    evader = role == "evader"

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d2 = best_res_dist2(nx, ny)
        if d2 is None:
            dist = abs(nx - ox) + abs(ny - oy)
            score = dist if evader else -dist
        else:
            # Prefer reducing distance to nearest resource; slight tie-break by moving consistently.
            score = -d2 + (0.001 * (dx * dy + dx + dy))
            if evader:
                score += 0.01 * (abs(nx - ox) + abs(ny - oy))
            else:
                score -= 0.01 * (abs(nx - ox) + abs(ny - oy))

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]