def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (w - 1, 0) if (sx + sy) > (ox + oy) else (0, h - 1)
        best = (10**9, (0, 0))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obst:
                continue
            d = man(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, (dx, dy))
        return [int(best[1][0]), int(best[1][1])]

    rlist = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
            rlist.append((rx, ry))
        except Exception:
            pass

    def best_adv_from(px, py):
        best = None
        for rx, ry in rlist:
            md = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; tie-break by smaller my distance.
            adv = md - od
            key = (adv, md, abs(rx - ox) + abs(ry - oy), rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[0] if best else (10**9, 10**9, 10**9, 0, 0)

    cur_key = best_adv_from(sx, sy)
    best_move = (0, 0)
    best_key = cur_key
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        k = best_adv_from(nx, ny)
        if k < best_key:
            best_key = k
            best_move = (dx, dy)
        elif k == best_key:
            # Deterministic tie-break: prefer moving closer to opponent.
            if man(nx, ny, ox, oy) < man(sx, sy, ox, oy):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]