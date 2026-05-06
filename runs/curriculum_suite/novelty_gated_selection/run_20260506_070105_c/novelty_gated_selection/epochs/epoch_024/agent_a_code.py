def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    scored = []
    for rx, ry in resources:
        od = man(ox, oy, rx, ry)
        scored.append((od, rx, ry))
    scored.sort()
    top = scored[:3]

    best = (float("-inf"), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        val = 0.0
        for od, rx, ry in top:
            md = man(nx, ny, rx, ry)
            if md == 0:
                val += 1000.0
            if md <= od:
                val += 80.0 - md
            else:
                val += max(-50.0, (od - md) * 3.0)
            val += 1.0 / (1.0 + md)

        if val > best[0]:
            best = (val, dx, dy)
    return [int(best[1]), int(best[2])]