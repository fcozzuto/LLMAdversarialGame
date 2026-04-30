def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = resources
    if not targets:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            for ddx, ddy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                tx, ty = sx + ddx, sy + ddy
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                    return [ddx, ddy]
        return [dx, dy]

    best = None
    best_key = None
    for r in targets:
        rd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        gain = rd - od
        key = (gain, rd, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = r
    tx, ty = best

    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    moves = [(dx, dy), (dx, 0), (0, dy), (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    seen = set()
    for ddx, ddy in moves:
        if (ddx, ddy) in seen:
            continue
        seen.add((ddx, ddy))
        nx, ny = sx + ddx, sy + ddy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # small anti-collision bias: prefer not getting closer to opponent when similar to target
            myd = dist((nx, ny), (tx, ty))
            opd = dist((nx, ny), (ox, oy))
            cur_opd = dist((sx, sy), (ox, oy))
            if myd == best_key[1] or opd >= cur_opd:
                return [ddx, ddy]
    for ddx, ddy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nx, ny = sx + ddx, sy + ddy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [ddx, ddy]
    return [0, 0]