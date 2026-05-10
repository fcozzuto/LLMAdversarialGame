def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx = int(sp[0]) if len(sp) > 0 else 0
    sy = int(sp[1]) if len(sp) > 1 else 0
    ox = int(op[0]) if len(op) > 0 else 0
    oy = int(op[1]) if len(op) > 1 else 0

    def parse_cells(key):
        s = set()
        for c in observation.get(key, []) or []:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                try:
                    s.add((int(c[0]), int(c[1])))
                except:
                    pass
        return s

    obstacles = parse_cells("obstacles")
    unclaimed = parse_cells("unclaimed_cells")
    opp_terr = parse_cells("opponent_territory")
    self_terr = parse_cells("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = moves[0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 6
        if (nx, ny) in self_terr:
            score += 2
        if (nx, ny) in opp_terr:
            score -= 6
        dcur = abs(sx - ox) + abs(sy - oy)
        dnew = abs(nx - ox) + abs(ny - oy)
        score += (dnew - dcur) * (-0.5)  # prefer increasing distance a bit
        if (nx, ny) == (ox, oy):
            score -= 100
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]