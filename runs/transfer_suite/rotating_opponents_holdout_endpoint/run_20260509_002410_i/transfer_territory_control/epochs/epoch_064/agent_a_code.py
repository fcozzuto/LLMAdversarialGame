def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
                if inside(x, y):
                    obstacles.add((x, y))
            except:
                pass

    targets = []
    for key in ("unclaimed_cells", "resources"):
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    x, y = int(p[0]), int(p[1])
                    if inside(x, y) and (x, y) not in obstacles:
                        targets.append((x, y))
                except:
                    pass
        if targets:
            break

    if not targets:
        targets = [(ox, oy)]

    # pick nearest target
    tx, ty = targets[0]
    bestd = (sx - tx) * (sx - tx) + (sy - ty) * (sy - ty)
    for (x, y) in targets[1:]:
        d = (sx - x) * (sx - x) + (sy - y) * (sy - y)
        if d < bestd:
            bestd = d
            tx, ty = x, y

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    bestm = (0, 0)
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # small bias to keep away from opponent unless targeting opponent
        away = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy) if (tx, ty) != (ox, oy) else 0
        score = -dist + 0.05 * away
        if bestscore is None or score > bestscore or (score == bestscore and (dx, dy) < bestm):
            bestscore = score
            bestm = (dx, dy)

    dx, dy = bestm
    return [int(dx), int(dy)]