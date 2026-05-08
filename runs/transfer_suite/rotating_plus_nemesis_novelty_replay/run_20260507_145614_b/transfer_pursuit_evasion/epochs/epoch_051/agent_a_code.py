def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict) and "position" in r:
            pr = r["position"]
            if isinstance(pr, (list, tuple)) and len(pr) >= 2:
                targets.append((int(pr[0]), int(pr[1])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx*dx + dy*dy

    if targets:
        tx, ty = min(targets, key=lambda p: dist2(sx, sy, p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = dist2(nx, ny, tx, ty)
        if v == 0 and (nx, ny) == (tx, ty):
            v -= 1000000
        if best_val is None or v < best_val or (v == best_val and (dx, dy) < best):
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]