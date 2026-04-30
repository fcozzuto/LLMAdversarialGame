def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", [])
    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    best = None
    best_score = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        score = (do - ds) * 100 - ds
        if best is None or score > best_score:
            best = (rx, ry)
            best_score = score

    tx, ty = best
    dx = tx - sx
    dy = ty - sy
    if dx:
        dx = 1 if dx > 0 else -1
    if dy:
        dy = 1 if dy > 0 else -1

    if dx != 0 and dy != 0:
        if man(sx + dx, sy, tx, ty) <= man(sx, sy + dy, tx, ty):
            dy = 0
        else:
            dx = 0

    if dx == 0 and dy == 0:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
    return [dx, dy]