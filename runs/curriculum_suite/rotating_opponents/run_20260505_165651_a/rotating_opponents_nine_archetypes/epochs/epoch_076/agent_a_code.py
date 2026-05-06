def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    raw_res = observation.get("resources") or []
    raw_obs = observation.get("obstacles") or []
    obs = set()
    for p in raw_obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            obs.add((p["x"], p["y"]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    res = []
    for r in raw_res:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = r["x"], r["y"]
        else:
            continue
        if inb(x, y) and (x, y) not in obs:
            res.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18
    if res:
        tx, ty = min(res, key=lambda p: (man(p[0], p[1], sx, sy), p[0], p[1]))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            dres = man(nx, ny, tx, ty)
            dreac = man(nx, ny, ox, oy)
            score = -dres + (0 if dreac == 0 else 0.1 / dreac) - 0.2 * dreac
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            dreac = man(nx, ny, ox, oy)
            score = dreac - 0.01 * (abs(nx - (w // 2)) + abs(ny - (h // 2)))
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]