def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue

        if (nx, ny) in unclaimed:
            base = 10000
        elif (nx, ny) in my_terr:
            base = 2000
        elif (nx, ny) in op_terr:
            base = -500
        else:
            base = 0

        d_op = abs(nx - ox) + abs(ny - oy)
        d_un = 0
        if unclaimed:
            d_un = min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed)

        val = base + (-d_un if unclaimed else 0) + (d_op * 3)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]