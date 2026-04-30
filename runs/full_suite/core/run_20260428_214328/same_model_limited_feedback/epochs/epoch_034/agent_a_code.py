def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy)

    best = None  # (score, tx, ty)
    if resources:
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            md = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Prefer resources where I'm not farther than opponent; break ties by closer md then coord.
            score = (md - od, md, rx, ry)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        _, tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    dx0 = 0
    dy0 = 0
    # Candidate deltas (including stay)
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx
            ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dist((nx, ny), (tx, ty)), -abs(dx), -abs(dy), nx, ny, dx, dy))
    # Deterministic: minimize distance to target; then prefer diagonal (via abs tie-break), then lex
    cand.sort()
    return [cand[0][-2], cand[0][-1]]