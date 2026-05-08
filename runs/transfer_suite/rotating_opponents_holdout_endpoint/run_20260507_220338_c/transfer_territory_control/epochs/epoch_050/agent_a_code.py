def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    def add_coords(iterable):
        s = []
        for p in iterable or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.append((int(p[0]), int(p[1])))
        return s

    obstacles = set(add_coords(observation.get("obstacles")))
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def pick_target():
        oppt = add_coords(observation.get("opponent_territory"))
        if oppt:
            mx = sum(x for x, _ in oppt) / len(oppt)
            my = sum(y for _, y in oppt) / len(oppt)
            return int(round(mx)), int(round(my))
        opp_pos = observation.get("opponent_position")
        if isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2:
            return int(opp_pos[0]), int(opp_pos[1])
        uc = add_coords(observation.get("unclaimed_cells"))
        if uc:
            mx = sum(x for x, _ in uc) / len(uc)
            my = sum(y for _, y in uc) / len(uc)
            return int(round(mx)), int(round(my))
        return (w - 1) // 2, (h - 1) // 2

    tx, ty = pick_target()

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        score = d * 10 + (0 if (dx == 0 and dy == 0) else 1)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [best[1], best[2]]