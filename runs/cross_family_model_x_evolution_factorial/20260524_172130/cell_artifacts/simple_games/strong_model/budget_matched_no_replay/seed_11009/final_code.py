def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    me = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    rx = observation.get("resources", [])
    obs = observation.get("obstacles", [])
    sx, sy = me[0], me[1]
    ox, oy = op[0], op[1]
    if isinstance(rx, dict):
        rx = list(rx)
    if isinstance(obs, dict):
        obs = list(obs)
    best = [0, 0]
    bestv = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if w and (nx < 0 or nx >= w):
                continue
            if h and (ny < 0 or ny >= h):
                continue
            blocked = False
            for p in obs:
                if isinstance(p, (list, tuple)) and len(p) >= 2 and p[0] == nx and p[1] == ny:
                    blocked = True
                    break
            if blocked:
                continue
            v = 0
            if rx:
                d = min(abs(nx - p[0]) + abs(ny - p[1]) for p in rx if isinstance(p, (list, tuple)) and len(p) >= 2)
                v -= d * 10
                if abs(dx) + abs(dy) == 0:
                    v -= 1
            else:
                v -= abs(nx - ox) + abs(ny - oy)
            v -= (abs(nx - ox) + abs(ny - oy)) // 2
            if dx == 0 and dy == 0:
                v -= 1
            if v > bestv:
                bestv = v
                best = [dx, dy]
    return best
