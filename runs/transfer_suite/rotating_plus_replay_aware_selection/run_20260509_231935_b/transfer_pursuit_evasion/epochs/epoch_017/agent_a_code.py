def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role") or "").lower()
    orr = str(observation.get("opponent_role") or "").lower()
    pursue = True
    if ("evad" in sr) or ("escape" in sr):
        pursue = False
    if ("evad" in orr) and ("purs" in sr):
        pursue = True
    if ("purs" in orr) and ("evad" in sr):
        pursue = False

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    best = None
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            d = dist(nx, ny)
            score = -d if pursue else d
            if dx == 0 and dy == 0:
                score -= 0.1
            if d == 0 and not pursue:
                score += 1000
            if d == 0 and pursue:
                score += 1000
            if best is None or score > best_score:
                best_score = score
                best = [dx, dy]
    if best is None:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if in_bounds(nx, ny) and (nx, ny) not in obs:
                    return [dx, dy]
        return [0, 0]
    return best