def choose_move(observation):
    w = int(observation.get("grid_width") or 0) or 8
    h = int(observation.get("grid_height") or 0) or 8
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                targets.append((x, y))
        except:
            pass
    if not targets:
        targets = [(w // 2, h // 2)]

    cx, cy = w // 2, h // 2
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1),(0,0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_val = -10**18
    ts = targets[:30]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = 0
        if ts:
            cand = (-10**18, None)
            for tx, ty in ts:
                dopp = md(nx, ny, ox, oy) + 0  # keep deterministic
                dtgt_opp = md(tx, ty, ox, oy)
                dtgt_us = md(nx, ny, tx, ty)
                val = (1000 - dtgt_opp) * 10 - dtgt_us
                if val > cand[0] or (val == cand[0] and (tx, ty) < cand[1]):
                    cand = (val, (tx, ty))
            v += cand[0]
        v += -md(nx, ny, cx, cy) * 2
        v -= (1 if (nx, ny) == (ox, oy) else 0) * 100000
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]