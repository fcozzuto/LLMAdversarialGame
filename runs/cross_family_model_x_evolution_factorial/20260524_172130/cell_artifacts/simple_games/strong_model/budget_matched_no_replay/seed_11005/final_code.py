def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    s = observation.get("self_position", (0, 0))
    o = observation.get("opponent_position", (0, 0))
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def pts(v):
        out = []
        if isinstance(v, dict):
            for k in v:
                out += pts(v[k])
        elif isinstance(v, (list, tuple)):
            if len(v) >= 2 and isinstance(v[0], (int, float)) and isinstance(v[1], (int, float)):
                out.append((int(v[0]), int(v[1])))
            else:
                for e in v:
                    out += pts(e)
        return out

    res = pts(observation.get("resources", []))
    obs = set(pts(observation.get("obstacles", [])))
    best = (0, 0)
    bestv = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or (w and nx >= w) or (h and ny >= h) or (nx, ny) in obs:
                continue
            v = 0
            if res:
                d = min(abs(nx - x) + abs(ny - y) for x, y in res)
                v -= d * 10
            else:
                d = abs(nx - ox) + abs(ny - oy)
                v += (4 - d) * 3
            if (nx, ny) == (ox, oy):
                v += 6
            if (sx, sy) == (ox, oy):
                v += 2
            if d == 0 if not res else False:
                pass
            if res:
                v -= abs(nx - ox) + abs(ny - oy)
            else:
                v -= abs(nx - ox) + abs(ny - oy) // 2
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
    return [int(best[0]), int(best[1])]
