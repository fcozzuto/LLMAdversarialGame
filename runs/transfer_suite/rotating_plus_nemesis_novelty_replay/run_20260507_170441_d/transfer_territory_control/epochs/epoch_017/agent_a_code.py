def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for p in (observation.get("resources") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    turn = int(observation.get("turn_index") or 0)
    late = turn >= 40

    if resources:
        tx, ty = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
    else:
        tx, ty = ox, oy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_res = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        score = d_res + (0.0 if not late else -0.3 * d_opp)
        score += 0.01 * ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best