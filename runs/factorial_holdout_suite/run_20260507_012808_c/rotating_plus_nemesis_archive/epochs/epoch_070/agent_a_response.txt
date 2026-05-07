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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        dx = 0 if sx == 0 else (-1 if sx > w - 1 - sx else 1)
        dx = 0 if sx <= w // 2 else (-1 if sx > w - 1 else 1)
        dy = 0 if sy <= h // 2 else (-1 if sy > h - 1 else 1)
        dx = -1 if sx > w // 2 else (1 if sx < w // 2 else 0)
        dy = -1 if sy > h // 2 else (1 if sy < h // 2 else 0)
        return [dx if dx in (-1, 0, 1) else 0, dy if dy in (-1, 0, 1) else 0]

    best = None
    best_val = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Maximize "you are closer than opponent"; tie-break toward nearer and safer cells
        val = (od - sd, -sd, - (abs(rx - sx) + abs(ry - sy)))
        if best_val is None or val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Deterministically sidestep: prefer axis that keeps closest to target
        cand = []
        for ddx, ddy in [(-dx, ddy), (ddx, -dy), (-dx, -dy), (dx, 0), (0, dy), (0, 0)]:
            if ddx is None: continue
            cx, cy = sx + ddx, sy + ddy
            if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in obstacles:
                cand.append((man(cx, cy, rx, ry), ddx, ddy))
        if cand:
            cand.sort(key=lambda t: (t[0], t[1], t[2]))
            _, dx, dy = cand[0]
        else:
            dx = 0
            dy = 0

    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]