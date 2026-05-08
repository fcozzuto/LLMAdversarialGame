def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                blocked.add((x, y))
        except: 
            pass

    self_term = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_term = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    targets = []
    if unclaimed:
        targets = list(unclaimed)
    else:
        targets = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]

    if not targets:
        targets = [(w // 2, h // 2)]

    best_score = -10**18
    best_move = (0, 0)
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        if (nx, ny) in opp_term:
            score = -1000000
        else:
            d_to_target = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            score = -d_to_target
            if (nx, ny) in self_term:
                score += 4
            if (nx, ny) in unclaimed:
                score += 8
            if abs(nx - ox) + abs(ny - oy) <= 1:
                score -= 3
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]