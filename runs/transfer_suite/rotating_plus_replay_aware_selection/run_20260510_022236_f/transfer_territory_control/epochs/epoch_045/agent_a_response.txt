def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    best = None  # (score, dx, dy)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d_self = abs(nx - sx) + abs(ny - sy)
        d_opp = man(nx, ny, ox, oy)

        score = 0
        if (nx, ny) in unclaimed:
            score += 1000
            score -= man(nx, ny, sx, sy) * 2
            score += d_opp * 3
        elif (nx, ny) in opp_terr:
            # Flipping on entry: stealing is valuable; prioritize moves that reduce opp distance.
            score += 900
            score += man(nx, ny, ox, oy) * 1
            score -= man(nx, ny, sx, sy) * 0.5
        else:
            # Prefer to expand/maintain space while avoiding the opponent.
            score += d_opp * 5
            score -= man(nx, ny, sx, sy) * 0.5

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]