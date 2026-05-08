def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    blocked = to_set("obstacles")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")
    unclaimed = to_set("unclaimed_cells")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_score = -10**18

    use_unclaimed = len(unclaimed) > 0
    u_list = list(unclaimed) if use_unclaimed else []

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        score = 0
        if (nx, ny) in opp_terr:
            score -= 1000
        if (nx, ny) in self_terr:
            score += 10
        if use_unclaimed:
            d = min(abs(nx - ux) + abs(ny - uy) for ux, uy in u_list)
            score += -d * 5
        else:
            score += - (abs(nx - ox) + abs(ny - oy))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]