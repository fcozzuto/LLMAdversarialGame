def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    scores = observation.get("scores") or {}
    if isinstance(scores, dict):
        self_score = scores.get("self", scores.get(0, 0))
        opp_score = scores.get("opponent", scores.get(1, 0))
    else:
        self_score, opp_score = 0, 0
    try:
        self_score = int(self_score)
        opp_score = int(opp_score)
    except:
        self_score, opp_score = 0, 0

    behind = self_score < opp_score

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d2o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if behind:
            val = (d2o, dx, dy)  # closer to opponent
        else:
            val = (-d2o, -dx, -dy)  # farther from opponent (safer)
        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best

    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]