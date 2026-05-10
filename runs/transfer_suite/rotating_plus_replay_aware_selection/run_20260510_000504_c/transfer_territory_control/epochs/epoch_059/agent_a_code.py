def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    resources = observation.get("resources") or []

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy
    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny): yield nx, ny

    if resources:
        targets = [tuple(r) for r in resources]
    else:
        boundary_opp = []
        for px, py in opp_terr:
            for nx, ny in neighbors(px, py):
                if (nx, ny) in unclaimed:
                    boundary_opp.append((px, py))
                    break
        if boundary_opp:
            targets = boundary_opp
        elif unclaimed:
            targets = list(unclaimed)
        else:
            targets = list(opp_terr) if opp_terr else [(w - 1, h - 1)]

    best_target = targets[0]
    bestd = dist(sx, sy, best_target[0], best_target[1])
    for tx, ty in targets:
        d = dist(sx, sy, tx, ty)
        if d < bestd or (d == bestd and (ty < best_target[1] or (ty == best_target[1] and tx < best_target[0]))):
            bestd, best_target = d, (tx, ty)

    tx, ty = best_target
    best_move = (0, 0)
    best_score = -10**9
    move_order = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dcur = dist(sx, sy, tx, ty)
        dnew = dist(nx, ny, tx, ty)
        score = (dcur - dnew) * 10
        if (nx, ny) in opp_terr: score += 35
        if (nx, ny) in unclaimed: score += 18
        if (nx, ny) in self_terr: score -= 4
        if (nx, ny) == (ox, oy): score -= 7
        # Prefer breaking toward opponent: reduce distance to opponent slightly when engaging
        if (nx, ny) in opp_terr or (nx, ny) in unclaimed:
            score += (dist(sx, sy, ox, oy) - dist(nx, ny, ox, oy)) * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]