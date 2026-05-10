def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx, dy = a - c, b - d
        return abs(dx) + abs(dy)

    best = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = dist(nx, ny, ox, oy)
        in_un = 1 if (nx, ny) in unclaimed else 0
        near_un = 0
        if unclaimed:
            for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) in unclaimed:
                    near_un = 1
                    break
        score = (in_un * 1000) + (near_un * 120) + (d_opp * 3) - (dist(nx, ny, sx, sy) * 1)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]