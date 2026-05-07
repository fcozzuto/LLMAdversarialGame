def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def ti(v):
        try:
            return int(v)
        except:
            return 0

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx = ti(sp[0]) if isinstance(sp, (list, tuple)) and len(sp) > 0 else 0
    sy = ti(sp[1]) if isinstance(sp, (list, tuple)) and len(sp) > 1 else 0
    ox = ti(op[0]) if isinstance(op, (list, tuple)) and len(op) > 0 else 0
    oy = ti(op[1]) if isinstance(op, (list, tuple)) and len(op) > 1 else 0

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
        elif isinstance(p, dict):
            x, y = ti(p.get("x")), ti(p.get("y"))
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = observation.get("resources") or []
    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = ti(r.get("x")), ti(r.get("y"))
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res_cells.append((x, y))

    if not res_cells:
        return [0, 0]

    best = None
    best_key = None
    for x, y in res_cells:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        key = (od - sd - (1 if sd == 0 else 0), -sd)
        if best is None or key > best_key:
            best = (x, y)
            best_key = key

    tx, ty = best
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Prefer reducing distance to target; break ties by increasing distance to opponent.
    best_m = (0, 0)
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = abs(tx - nx) + abs(ty - ny)
        od2 = abs(tx - ox) + abs(ty - oy)
        # Also slightly avoid moving away from target
        v = (-sd2, (od2 - (abs(tx - ox) + abs(ty - oy))), abs(nx - tx) + abs(ny - ty), -(dx*dx+dy*dy))
        if best_v is None or v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]