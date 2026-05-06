def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    closest = None
    bestd = 10**18
    for r in resources:
        if isinstance(r, dict):
            rx, ry = r.get("position", (None, None))
            if rx is None:
                continue
        else:
            if not (isinstance(r, (list, tuple)) and len(r) == 2):
                continue
            rx, ry = r[0], r[1]
        if (rx, ry) in blocked:
            continue
        d = md(sx, sy, rx, ry)
        if d < bestd or (d == bestd and (rx, ry) < closest):
            bestd = d
            closest = (rx, ry)

    target = closest if closest is not None else (ox, oy)

    best = None
    bestscore = 10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = md(nx, ny, target[0], target[1])
        adv = -md(nx, ny, ox, oy)
        score = d * 2 + (-adv)
        if score < bestscore or (score == bestscore and (dx, dy) < best):
            bestscore = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]