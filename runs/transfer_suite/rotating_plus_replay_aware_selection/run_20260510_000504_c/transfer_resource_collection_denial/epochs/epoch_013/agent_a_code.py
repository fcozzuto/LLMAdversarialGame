def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                res.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))
    res = [p for p in res if p not in obstacles]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not res:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return [0, 0]
        return [dx, dy]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def score_cell(tx, ty):
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        adv = od - sd
        return (adv, -sd, -tx, -ty)

    target = max(res, key=lambda p: score_cell(p[0], p[1]))
    tx, ty = target

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                deltas.append((dx, dy))
    if not deltas:
        return [0, 0]

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        # Prefer reducing distance, then keep move diagonal if tied, then lex order by (dx,dy)
        dist_now = md(sx, sy, tx, ty)
        dist_next = md(nx, ny, tx, ty)
        diag = 1 if dx != 0 and dy != 0 else 0
        key = (dist_next < dist_now, dist_now - dist_next, diag, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    return best[1]