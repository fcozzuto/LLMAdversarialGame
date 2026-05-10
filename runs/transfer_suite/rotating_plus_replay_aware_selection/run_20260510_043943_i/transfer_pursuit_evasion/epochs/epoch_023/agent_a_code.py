def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role or "hunter" in self_role or "chaser" in self_role or "guard" in self_role or ("evader" not in self_role))

    if sx == ox and sy == oy:
        return [0, 0]

    res = observation.get("resources") or []
    rpos = []
    for r in res:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rpos.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) == 2:
                a, b = r["position"]
                rpos.append((int(a), int(b)))
            elif "x" in r and "y" in r:
                rpos.append((int(r["x"]), int(r["y"])))

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    target = (ox, oy)
    if rpos:
        tx, ty = min(rpos, key=lambda p: d2(sx, sy, p[0], p[1]))
        target = (tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if rpos:
            score = d2(nx, ny, target[0], target[1])
        else:
            score = d2(nx, ny, ox, oy)
            score = score if pursuer else -score
        score = (score, abs(dx), abs(dy), dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]