def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((x, y))
        except:
            pass
    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            x, y = p
            res.append((x, y))
        except:
            pass
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_opp = man(nx, ny, ox, oy)
        if res:
            d_res = min(man(nx, ny, rx, ry) for rx, ry in res)
        else:
            d_res = 10**9
        score = 0
        if (nx, ny) in res:
            score += 5000
        score += (-d_opp) * 3
        score += (-d_res) * 2
        if (nx, ny) in selfT:
            score += 50
        elif (nx, ny) in oppT:
            score -= 80
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best