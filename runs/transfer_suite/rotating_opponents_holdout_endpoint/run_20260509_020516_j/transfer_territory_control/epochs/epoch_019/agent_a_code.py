def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
            else:
                x, y = int(p.get("x", 0)), int(p.get("y", 0))
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))
        except Exception:
            pass

    opp_tr = set(tuple(t) for t in (observation.get("opponent_territory") or []))

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    unclaimed = list(observation.get("unclaimed_cells") or [])
    goals = []
    for c in unclaimed:
        try:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < W and 0 <= y < H and (x, y) != (sx, sy) and (x, y) not in opp_tr:
                goals.append((x, y))
        except Exception:
            pass

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
    best = None
    best_score = None

    if goals:
        # Aim for the closest safe unclaimed cell.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = min(abs(gx - nx) + abs(gy - ny) for gx, gy in goals)
            score = (dist, (nx, ny) == (ox, oy))
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]
    else:
        # Otherwise move to reduce distance to opponent, avoiding opponent territory.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny) or (nx, ny) in opp_tr:
                continue
            dist = abs(ox - nx) + abs(oy - ny)
            score = (dist, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best