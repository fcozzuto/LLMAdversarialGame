def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def parse_cells(key):
        out = []
        for c in observation.get(key) or []:
            if c and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                    out.append((x, y))
        return out

    unclaimed = parse_cells("unclaimed_cells")
    opp_t = parse_cells("opponent_territory")
    candidates = []
    our_cnt = int(observation.get("self_territory_count") or 0)
    opp_cnt = int(observation.get("opponent_territory_count") or 0)
    if opp_t or unclaimed:
        candidates = unclaimed if our_cnt < opp_cnt and unclaimed else (opp_t if opp_t else unclaimed)
    if not candidates:
        candidates = [(ox, oy)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        d = min(manh(nx, ny, tx, ty) for tx, ty in candidates)
        score = -d
        if (nx, ny) == (ox, oy):
            score += 1
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]