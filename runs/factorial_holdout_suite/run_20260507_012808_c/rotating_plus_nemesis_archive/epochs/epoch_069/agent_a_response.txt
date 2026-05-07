def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        dx = 0 if sx <= w // 2 else (-1 if sx > w // 2 else 1)
        dy = 0 if sy <= h // 2 else (-1 if sy > h // 2 else 1)
        if dx < -1:
            dx = -1
        if dx > 1:
            dx = 1
        if dy < -1:
            dy = -1
        if dy > 1:
            dy = 1
        return [dx, dy]

    best = None
    best_score = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can secure: maximize (opp_closer_by - our_closer_by), then closer to us
        score = (do - ds, -ds)
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # If blocked by going to obstacle next step, try axis move deterministically
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        if (sx + dx, sy) not in obstacles:
            dy = 0
        elif (sx, sy + dy) not in obstacles:
            dx = 0
        else:
            dx = 0
            dy = 0

    return [int(dx), int(dy)]