def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): unclaimed.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if unclaimed:
        best_u = None
        best_d = 10**9
        for ux, uy in unclaimed:
            d = abs(ux - sx) + abs(uy - sy)
            if d < best_d or (d == best_d and (ux, uy) < best_u):
                best_d = d
                best_u = (ux, uy)
        tx, ty = best_u
    else:
        tx = 0 if (sx + sy) >= (ox + oy) else w - 1
        ty = 0 if (sx + sy) < (ox + oy) else h - 1

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to_target = abs(tx - nx) + abs(ty - ny)
        dist_to_opp = abs(ox - nx) + abs(oy - ny)
        score = (-dist_to_target) + 0.15 * dist_to_opp
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not inb(sx + dx, sy + dy) or (sx + dx, sy + dy) in obstacles:
        return [0, 0]
    return [dx, dy]