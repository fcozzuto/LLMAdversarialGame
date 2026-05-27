def choose_move(observation):
    W = observation.get("grid_width", 0)
    H = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    scores = observation.get("scores", [0, 0])
    me = scores[0] if isinstance(scores, (list, tuple)) and scores else 0
    opp = scores[1] if isinstance(scores, (list, tuple)) and len(scores) > 1 else 0

    def pts(v):
        out = []
        if isinstance(v, dict):
            for x in v.values():
                out += pts(x)
        elif isinstance(v, (list, tuple)):
            if len(v) >= 2 and isinstance(v[0], (int, float)) and isinstance(v[1], (int, float)):
                out.append((int(v[0]), int(v[1])))
            else:
                for x in v:
                    out += pts(x)
        return out

    res = pts(resources)
    obs = set(pts(obstacles))
    best = (0, 0)
    bestv = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= W or ny >= H or (nx, ny) in obs:
                continue
            v = -3 * (abs(nx - ox) + abs(ny - oy)) + (me - opp)
            if res:
                d = min(abs(nx - x) + abs(ny - y) for x, y in res)
                v += 20 - 4 * d
                if (nx, ny) in res:
                    v += 50
            else:
                v += -(abs(nx - (W - 1)) + abs(ny - (H - 1)))
            if dx == 0 and dy == 0:
                v -= 1
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
    return [best[0], best[1]]
