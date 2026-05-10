def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))
    resources = [p for p in resources if p not in obstacles]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        def md(ax, ay, bx, by):
            return abs(ax - bx) + abs(ay - by)
        # Prefer resources where we are closer than the opponent (my-op smallest).
        best = None
        best_key = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            key = (myd - opd, myd)  # smaller is better
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    def move_score(nx, ny):
        d0 = abs(sx - tx) + abs(sy - ty)
        d1 = abs(nx - tx) + abs(ny - ty)
        # Primary: get closer to chosen target; Secondary: avoid moving into "danger" (obstacles handled externally)
        return (d1, 0 if d1 <= d0 else 1, -1 if nx != sx and ny != sy else 0)

    best_move = (0, 0)
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = move_score(nx, ny)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]